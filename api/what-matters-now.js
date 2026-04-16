const CACHE_TTL_MS = 24 * 60 * 60 * 1000;
const responseCache = globalThis.__whatMattersNowCache || new Map();
globalThis.__whatMattersNowCache = responseCache;

export default async function handler(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return res.status(405).json({ error: "Method not allowed." });
  }

  const apiKey = process.env.GNEWS_API_KEY || "";
  if (!apiKey) {
    return res.status(500).json({ error: "GNews is not configured yet." });
  }

  const cacheKey = "global-signal";
  const cached = responseCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
    res.setHeader("Cache-Control", "s-maxage=86400, stale-while-revalidate=43200");
    return res.status(200).json(cached.data);
  }

  try {
    const url = "https://gnews.io/api/v4/top-headlines?category=general" +
      "&lang=en" +
      "&max=12" +
      "&apikey=" + encodeURIComponent(apiKey);

    const response = await fetch(url);
    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({
        error: "GNews returned " + response.status + ". " + text.slice(0, 180)
      });
    }

    const payload = await response.json();
    const stories = chooseStories(normalize(payload.articles || [])).slice(0, 3);
    responseCache.set(cacheKey, {
      timestamp: Date.now(),
      data: stories
    });

    res.setHeader("Cache-Control", "s-maxage=86400, stale-while-revalidate=43200");
    return res.status(200).json(stories);
  } catch (error) {
    if (cached && cached.data && cached.data.length) {
      res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate=43200");
      return res.status(200).json(cached.data);
    }

    return res.status(500).json({
      error: error.message || "Unable to load the current signal."
    });
  }
}

function normalize(articles) {
  const seen = new Set();
  return articles
    .map((article) => ({
      title: article.title || "",
      description: article.description || "",
      url: article.url || "",
      source: article.source && article.source.name ? article.source.name : "Source",
      publishedAt: article.publishedAt || ""
    }))
    .filter((article) => article.title && article.url)
    .filter((article) => {
      const key = article.url || article.title.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

function chooseStories(articles) {
  return articles
    .map((article) => ({ article, score: score(article) }))
    .sort((a, b) => b.score - a.score)
    .map((entry) => entry.article);
}

function score(article) {
  const text = (article.title + " " + article.description).toLowerCase();
  let value = 0;

  if (/policy|law|regulation|government|election|tariff|trade/.test(text)) value += 4;
  if (/economy|inflation|interest rate|market|earnings|funding/.test(text)) value += 4;
  if (/technology|ai|chip|software|platform|security/.test(text)) value += 3;
  if (/celebrity|viral|gossip|feud|rumor|outrage/.test(text)) value -= 5;
  if (article.description) value += 2;

  const published = new Date(article.publishedAt).getTime();
  if (!Number.isNaN(published)) {
    const ageHours = Math.max((Date.now() - published) / 36e5, 1);
    value += Math.max(8 - ageHours / 6, 0);
  }

  return value;
}

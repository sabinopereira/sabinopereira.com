const CACHE_TTL_MS = 10 * 60 * 1000;
const responseCache = globalThis.__quietNewsCache || new Map();
globalThis.__quietNewsCache = responseCache;

export default async function handler(req, res) {
  if (req.method === "GET") {
    return res.status(200).json({
      ok: Boolean(process.env.GNEWS_API_KEY),
      provider: "gnews"
    });
  }

  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    return res.status(405).json({ error: "Method not allowed." });
  }

  try {
    const preferences = typeof req.body === "string" ? JSON.parse(req.body) : req.body || {};
    const apiKey = process.env.GNEWS_API_KEY || "";
    const cacheKey = JSON.stringify({
      selectedInterests: preferences.selectedInterests || [],
      customTopic: preferences.customTopic || "",
      language: preferences.language || "en",
      coverageType: preferences.coverageType || "mixed",
      regionFocus: preferences.regionFocus || "pt",
      timeFrame: preferences.timeFrame || "today"
    });

    if (!apiKey) {
      return res.status(500).json({
        error: "GNews is not configured yet. Add GNEWS_API_KEY in the deployment environment first."
      });
    }

    const cached = responseCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
      res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=300");
      return res.status(200).json(cached.data);
    }

    const requests = buildProviderRequests(preferences, apiKey);
    const rawResults = await Promise.all(
      requests.map(async (url) => {
        const response = await fetch(url);
        if (!response.ok) {
          const text = await response.text();
          const error = new Error("GNews returned " + response.status + ". " + text.slice(0, 180));
          error.status = response.status;
          throw error;
        }
        return response.json();
      })
    );

    const articles = normalizeResults(rawResults.flatMap((result) => normalizeProviderPayload(result)));
    responseCache.set(cacheKey, {
      timestamp: Date.now(),
      data: articles
    });

    res.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=300");
    return res.status(200).json(articles);
  } catch (error) {
    if (error.status === 429) {
      return res.status(429).json({
        error: "Quiet Signal is receiving too many requests right now. Please wait a moment and try again."
      });
    }

    return res.status(error.status || 500).json({
      error: error.message || "Unable to build the news briefing right now."
    });
  }
}

function mapLanguage(language) {
  return language === "pt" ? "pt" : "en";
}

function getDateRange(timeFrame) {
  const now = new Date();
  const end = new Date(now);
  const start = new Date(now);

  if (timeFrame === "today") {
    start.setHours(0, 0, 0, 0);
  } else if (timeFrame === "yesterday") {
    start.setDate(start.getDate() - 1);
    start.setHours(0, 0, 0, 0);
    end.setDate(end.getDate() - 1);
    end.setHours(23, 59, 59, 999);
  } else if (timeFrame === "this-week") {
    const day = start.getDay();
    const diff = day === 0 ? 6 : day - 1;
    start.setDate(start.getDate() - diff);
    start.setHours(0, 0, 0, 0);
  } else {
    start.setDate(start.getDate() - 7);
    start.setHours(0, 0, 0, 0);
  }

  return { start, end };
}

function buildQuery(preferences) {
  const interestSearchTerms = {
    "AI / Tech": "AI technology",
    "Business / Economy": "business economy",
    "World / Geopolitics": "geopolitics world",
    "Science / Health": "science health",
    "Culture / Entertainment": "culture entertainment",
    "Environment / Climate": "climate environment",
    "Books / Ideas": "books ideas",
    Sports: "sports"
  };

  const selectedInterests = Array.isArray(preferences.selectedInterests) ? preferences.selectedInterests : [];
  const interestTerms = selectedInterests
    .slice(0, 3)
    .map((interest) => interestSearchTerms[interest] || String(interest || "").trim())
    .filter(Boolean);
  const customTopic = String(preferences.customTopic || "")
    .trim()
    .slice(0, 60);
  if (customTopic) interestTerms.unshift(customTopic);
  const query = interestTerms.join(" OR ");
  return query.slice(0, 180);
}

function buildProviderRequests(preferences, apiKey) {
  const query = encodeURIComponent(buildQuery(preferences));
  const language = mapLanguage(preferences.language || "en");
  const { start, end } = getDateRange(preferences.timeFrame || "today");
  const startIso = start.toISOString();
  const endIso = end.toISOString();
  const localCountry = preferences.regionFocus === "global" ? "" : (preferences.regionFocus || "pt");
  const requests = [];

  function pushRequest(mode) {
    let url = "https://gnews.io/api/v4/search?q=" + query +
      "&lang=" + language +
      "&max=20" +
      "&from=" + encodeURIComponent(startIso) +
      "&to=" + encodeURIComponent(endIso) +
      "&apikey=" + encodeURIComponent(apiKey);
    if (mode === "local" && localCountry && localCountry !== "eu") {
      url += "&country=" + encodeURIComponent(localCountry);
    }
    requests.push(url);
  }

  if (preferences.coverageType === "mixed") {
    pushRequest("global");
    pushRequest("local");
  } else if (preferences.coverageType === "local") {
    pushRequest("local");
  } else {
    pushRequest("global");
  }

  return requests.filter(Boolean);
}

function normalizeProviderPayload(payload) {
  return (payload.articles || []).map((article) => ({
    title: article.title || "",
    description: article.description || "",
    content: article.content || "",
    url: article.url || "",
    source: article.source && article.source.name ? article.source.name : "Source",
    publishedAt: article.publishedAt || ""
  }));
}

function normalizeResults(articles) {
  const seen = new Set();
  return articles
    .filter((article) => article.title && article.url)
    .filter((article) => {
      const key = article.url || article.title.toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

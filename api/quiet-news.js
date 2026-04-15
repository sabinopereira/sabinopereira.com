export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }

  try {
    const preferences = typeof req.body === "string" ? JSON.parse(req.body) : req.body || {};
    const apiKey = process.env.GNEWS_API_KEY || "";

    if (!apiKey) {
      return res.status(500).json({
        error: "GNews is not configured yet. Add GNEWS_API_KEY in the deployment environment first."
      });
    }

    const requests = buildProviderRequests(preferences, apiKey);
    const rawResults = await Promise.all(
      requests.map(async (url) => {
        const response = await fetch(url);
        if (!response.ok) {
          const text = await response.text();
          throw new Error("GNews returned " + response.status + ". " + text.slice(0, 180));
        }
        return response.json();
      })
    );

    const articles = normalizeResults(rawResults.flatMap((result) => normalizeProviderPayload(result)));

    return res.status(200).json(articles);
  } catch (error) {
    return res.status(500).json({
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
    "AI / Tech": "AI OR artificial intelligence OR technology OR software",
    "Business / Economy": "business OR economy OR markets OR companies",
    "World / Geopolitics": "geopolitics OR world OR international OR security",
    "Science / Health": "science OR health OR medicine OR research",
    "Culture / Entertainment": "culture OR media OR film OR entertainment",
    "Environment / Climate": "climate OR environment OR energy",
    "Books / Ideas": "books OR ideas OR publishing OR education",
    Sports: "sports OR football OR basketball OR tennis"
  };

  const selectedInterests = Array.isArray(preferences.selectedInterests) ? preferences.selectedInterests : [];
  const interestTerms = selectedInterests.map((interest) => interestSearchTerms[interest] || interest);
  if (preferences.customTopic) interestTerms.push(preferences.customTopic);
  return interestTerms.join(" OR ");
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

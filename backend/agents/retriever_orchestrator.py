import os
import math
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

SOURCE_BASE_CREDIBILITY = {
    "reuters": 0.95,
    "bloomberg": 0.9,
    "forbes": 0.85,
    "google news": 0.75,
    "techcrunch": 0.8,
    "twitter": 0.6,
    "linkedin": 0.65,
    "opencorporates": 0.7,
    "crunchbase": 0.8,
    "sec filings": 0.9,
    "facebook": 0.6,
    "academic": 0.75,
    "property": 0.65,
    "court records": 0.85,
    "google": 0.7,
    "unknown": 0.5
}

def apply_time_decay(base_score: float, published: str, decay_rate=0.01) -> float:
    try:
        pub_date = datetime.strptime(published[:10], "%Y-%m-%d")
        age_days = (datetime.utcnow() - pub_date).days
        return round(base_score * math.exp(-decay_rate * age_days), 4)
    except Exception:
        return round(base_score, 4)

def serpapi_search(entity: str, site_filter: str = "", fallback_used=False):
    print(f"🔍 SerpAPI search: {entity} within {site_filter if site_filter else 'all sites'}")
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f"{entity} {site_filter}".strip(),
        "api_key": SERPAPI_KEY,
        "num": 10
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for section in ["top_stories", "news_results", "organic_results"]:
            section_data = data.get(section, [])
            print(f"📦 Found {len(section_data)} items in {section}")
            for r in section_data:
                title = r.get("title") or r.get("name")
                snippet = r.get("snippet") or r.get("description", "")
                link = r.get("link") or r.get("url")
                published = (
                    r.get("date") or 
                    r.get("published_date") or 
                    datetime.utcnow().strftime("%Y-%m-%d")
                )

                if title and link:
                    source_name = (
                        site_filter.split(":")[1] if ":" in site_filter else
                        site_filter.split(".")[0] if "." in site_filter else
                        "google"
                    )
                    results.append({
                        "source": source_name,
                        "title": title,
                        "snippet": snippet,
                        "link": link,
                        "published": published
                    })

        # 🧯 If no results and this was google news, fallback to general search once
        if not results and site_filter == "site:news.google.com" and not fallback_used:
            print("⚠️ No results from google news — retrying with general Google search...")
            return serpapi_search(entity, "", fallback_used=True)

        if not results:
            print("⚠️ SerpAPI returned no results across all sections.")

        return results

    except Exception as e:
        print(f"❌ SerpAPI error for {site_filter}:", e)
        return []


    except Exception as e:
        print(f"❌ SerpAPI error for {site_filter}:", e)
        return []

def opencorporates_api_retrieval(entity: str):
    print(f"🏢 Fetching OpenCorporates for: {entity}")
    try:
        url = f"https://api.opencorporates.com/v0.4/companies/search"
        params = {"q": entity}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", {}).get("companies", [])
        return [
            {
                "source": "opencorporates",
                "title": c["company"].get("name", "Unknown Company"),
                "snippet": c["company"].get("company_number", ""),
                "link": c["company"].get("opencorporates_url"),
                "published": c["company"].get("incorporation_date", datetime.utcnow().strftime("%Y-%m-%d"))
            } for c in results
        ]
    except Exception as e:
        print("❌ OpenCorporates API error:", e)
        return []

SOURCE_RETRIEVERS = {
    "google news": lambda e: serpapi_search(e, "site:news.google.com"),
    "linkedin": lambda e: serpapi_search(e, "site:linkedin.com/in"),
    "twitter": lambda e: serpapi_search(e, "site:twitter.com"),
    "facebook": lambda e: serpapi_search(e, "site:facebook.com"),
    "academic": lambda e: serpapi_search(e, "site:nature.com OR site:researchgate.net OR site:scholar.google.com"),
    "court records": lambda e: serpapi_search(e, "site:courtlistener.com"),
    "property": lambda e: serpapi_search(e, "site:gov.propertyrecords.org"),
    "google search": lambda e: serpapi_search(e, ""),
    "sec filings": lambda e: serpapi_search(e, "site:sec.gov/edgar"),
    "bloomberg": lambda e: serpapi_search(e, "site:bloomberg.com"),
    "reuters": lambda e: serpapi_search(e, "site:reuters.com"),
    "techcrunch": lambda e: serpapi_search(e, "site:techcrunch.com"),
    "forbes": lambda e: serpapi_search(e, "site:forbes.com"),
    "crunchbase": lambda e: serpapi_search(e, "site:crunchbase.com"),
    "opencorporates": opencorporates_api_retrieval
}

def multi_source_retrieval(entity: str, plan: list) -> list:
    results = []
    for task in plan:
        raw_source = task.get("source", "").strip().lower()
        print(f"📡 Trying to retrieve from: {raw_source}")

        retriever = SOURCE_RETRIEVERS.get(raw_source)
        if retriever:
            try:
                retrieved = retriever(entity)
                base_score = SOURCE_BASE_CREDIBILITY.get(raw_source, 0.5)

                for chunk in retrieved:
                    pub_date_str = chunk.get("published", datetime.utcnow().strftime("%Y-%m-%d"))
                    chunk["credibility_score"] = base_score
                    chunk["time_decay_score"] = apply_time_decay(base_score, pub_date_str)

                print(f"✅ {len(retrieved)} results from {raw_source}")
                results.extend(retrieved)
            except Exception as e:
                print(f"❌ Error retrieving from {raw_source}: {e}")
        else:
            print(f"⚠️ No retriever mapped for: {raw_source}")
    return results

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

def normalize_published_date(raw_date: str) -> str:
    """
    Normalize relative dates like '2 hours ago' or '1 day ago' to today's date.
    If it's already in ISO format (YYYY-MM-DD), return it directly.
    """
    if not raw_date:
        return datetime.utcnow().strftime("%Y-%m-%d")

    try:
        # If it's already ISO-formatted, return it
        datetime.strptime(raw_date[:10], "%Y-%m-%d")
        return raw_date[:10]
    except ValueError:
        # Fallback: treat relative times like "5 hours ago" as "today"
        return datetime.utcnow().strftime("%Y-%m-%d")

def google_news_retrieval(entity: str, num_results=5):
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("❌ SERPAPI_KEY not found in environment variables.")
        return []

    search_url = "https://serpapi.com/search"

    params = {
        "q": entity,
        "tbm": "nws",
        "api_key": api_key,
        "num": num_results
    }

    response = requests.get(search_url, params=params)

    if response.status_code == 200:
        results = response.json().get("news_results", [])
        formatted = [{
            "source": "Google News",
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link"),
            "published": normalize_published_date(item.get("date") or item.get("published"))
        } for item in results]

        return formatted
    else:
        print(f"❌ SerpAPI error: {response.status_code} - {response.text}")
        return []

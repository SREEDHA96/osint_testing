from .retrieval.google_news import google_news_retrieval
from datetime import datetime
import math

# Credibility scores
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
    except Exception as e:
        print(f"⚠️ Failed to apply decay: {e}")
        return round(base_score, 4)

# Stubbed retrieval functions for illustration
def linkedin_retrieval(entity: str):
    return [{
        "source": "LinkedIn", "title": f"LinkedIn Profile of {entity}", "snippet": "Employment at XYZ Corp",
        "link": "https://linkedin.com/...", "published": "2024-12-01"
    }]

def twitter_retrieval(entity: str):
    return [{
        "source": "Twitter", "title": f"Tweets by {entity}", "snippet": "Public opinions and network",
        "link": "https://twitter.com/...", "published": "2025-06-08"
    }]

def facebook_retrieval(entity: str):
    return [{
        "source": "Facebook", "title": f"Facebook profile of {entity}", "snippet": "Photos and posts",
        "link": "https://facebook.com/...", "published": "2024-11-01"
    }]

def opencorporates_retrieval(entity: str):
    return [{
        "source": "OpenCorporates", "title": f"Company affiliations of {entity}", "snippet": "Director at ABC Ltd",
        "link": "https://opencorporates.com/...", "published": "2023-09-10"
    }]

def academic_retrieval(entity: str):
    return [{
        "source": "Academic", "title": f"Research by {entity}", "snippet": "Published in Nature",
        "link": "https://researchgate.net/...", "published": "2022-10-01"
    }]

def court_record_retrieval(entity: str):
    return [{
        "source": "Court Records", "title": f"Legal records for {entity}", "snippet": "No public litigation found",
        "link": "https://court.gov/...", "published": "2021-05-01"
    }]

def property_retrieval(entity: str):
    return [{
        "source": "Property", "title": f"Assets linked to {entity}", "snippet": "Owns residential property in Tehran",
        "link": "https://realestate.gov/...", "published": "2024-07-01"
    }]

def google_search_retrieval(entity: str):
    return [{
        "source": "Google", "title": f"Web mentions of {entity}", "snippet": "Seen in academic conference",
        "link": "https://example.com/...", "published": "2023-06-01"
    }]

SOURCE_RETRIEVERS = {
    "google news": google_news_retrieval,
    "linkedin": linkedin_retrieval,
    "twitter": twitter_retrieval,
    "twitter/x": twitter_retrieval,
    "facebook": facebook_retrieval,
    "opencorporates": opencorporates_retrieval,
    "academic": academic_retrieval,
    "academic databases": academic_retrieval,
    "court records": court_record_retrieval,
    "property records": property_retrieval,
    "google search": google_search_retrieval,
    # Stubs for sources not yet implemented
    "sec filings": lambda e: [],
    "bloomberg": lambda e: [],
    "techcrunch": lambda e: [],
    "reuters": lambda e: [],
    "crunchbase": lambda e: [],
    "forbes": lambda e: [],
}

# Main orchestrator
def multi_source_retrieval(entity: str, plan: list) -> list:
    results = []
    for task in plan:
        raw_source = task.get("source", "").strip().lower()
        print(f"📡 Trying to retrieve from: {raw_source}")
        
        retriever = SOURCE_RETRIEVERS.get(raw_source)
        if retriever:
            try:
                retrieved = retriever(entity)
                source_name = raw_source
                base_score = SOURCE_BASE_CREDIBILITY.get(source_name, 0.5)

                for chunk in retrieved:
                    pub_date = chunk.get("published", datetime.utcnow().strftime("%Y-%m-%d"))
                    chunk["credibility_score"] = base_score
                    chunk["time_decay_score"] = apply_time_decay(base_score, pub_date)

                print(f"✅ {len(retrieved)} results from {raw_source}")
                results.extend(retrieved)
            except Exception as e:
                print(f"❌ Error retrieving from {raw_source}: {e}")
        else:
            print(f"⚠️ No retriever mapped for: {raw_source}")
    return results

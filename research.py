import os
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
NEBIUS_API_URL = "https://api.studio.nebius.ai/v1/chat/completions"

# =========================
# 🔍 SEARCH FUNCTION (FALLBACK: DUCKDUCKGO)
# =========================
def quick_search(query, num_results=5):
    """
    Perform search using SerpAPI (if key available) or fallback to DuckDuckGo.
    """
    if SERPAPI_KEY:
        from serpapi import GoogleSearch
        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results
        })
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        return [
            {"title": r.get("title"), "link": r.get("link"), "snippet": r.get("snippet")}
            for r in organic_results
        ]
    else:
        # ✅ Free fallback: DuckDuckGo Instant Answer API
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        r = requests.get(url)
        data = r.json()
        results = []
        if "RelatedTopics" in data:
            for t in data["RelatedTopics"][:num_results]:
                if "Text" in t and "FirstURL" in t:
                    results.append({
                        "title": t["Text"],
                        "link": t["FirstURL"],
                        "snippet": t["Text"]
                    })
        return results

# =========================
# 🧠 SUMMARIZATION (Nebius)
# =========================
def summarize_text(text, max_tokens=300):
    """
    Summarize given text using DeepSeek model on Nebius API.
    """
    if not NEBIUS_API_KEY:
        return "❌ No Nebius key found. Please add NEBIUS_API_KEY in .env"

    headers = {
        "Authorization": f"Bearer {NEBIUS_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-0528",  # ✅ Working DeepSeek model
        "messages": [
            {"role": "system", "content": "You are a professional researcher. Summarize texts clearly and concisely."},
            {"role": "user", "content": f"Summarize this text:\n{text}"}
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens
    }

    response = requests.post(NEBIUS_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    else:
        return f"❌ Nebius summarization error: {response.status_code} - {response.text}"


# 🔗 COMBINED FUNCTION: SEARCH + SUMMARIZE
# =========================
def search_and_summarize(query, num_results=5):
    """
    Perform a search and then summarize the top results.
    Returns dict: {"summary": str, "sources": list}
    """
    results = quick_search(query, num_results=num_results)
    if not results:
        return {"summary": "❌ No search results found.", "sources": []}

    # Collect snippets for summarization
    combined_text = " ".join([r["snippet"] for r in results if r.get("snippet")])
    summary = summarize_text(combined_text)

    return {
        "summary": summary,
        "sources": results
    }

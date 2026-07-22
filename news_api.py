# NewsAPI wrappers for synchronous and asynchronous fetching.
# Keeps the article retrieval logic separate from the summarizer.
# Shares the same endpoint and query shape across both paths.
import requests
import aiohttp
from config import CONFIG

class NewsFetcher:
    # Store the API key and base URL for the sync fetcher.
    def __init__(self):
        self.api_key = CONFIG["NEWS_API_KEY"]
        self.base_url = "https://newsapi.org/v2"

    # Fetch technology headlines with the requests library.
    def fetch_top_tech_news(self, limit=3):
        url = f"{self.base_url}/top-headlines"
        params = {"category": "technology", "language": "en", "pageSize": limit, "apiKey": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
            response.raise_for_status()
            return response.json().get("articles", [])
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to fetch news. Details: {e}")
            return []

class AsyncNewsFetcher:
    """Asynchronous news fetcher using aiohttp."""
    # Store the API key and base URL for the async fetcher.
    def __init__(self):
        self.api_key = CONFIG["NEWS_API_KEY"]
        self.base_url = "https://newsapi.org/v2"

    # Fetch technology headlines with aiohttp.
    async def fetch_top_tech_news(self, limit=3):
        url = f"{self.base_url}/top-headlines"
        params = {"category": "technology", "language": "en", "pageSize": str(limit), "apiKey": self.api_key}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=CONFIG["REQUEST_TIMEOUT"]) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("articles", [])
            except Exception as e:
                print(f"ERROR: Failed to fetch news via aiohttp. Details: {e}")
                return []

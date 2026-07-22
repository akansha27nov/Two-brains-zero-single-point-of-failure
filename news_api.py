import requests
from config import CONFIG

class NewsFetcher:
    def __init__(self):
        self.api_key = CONFIG["NEWS_API_KEY"]
        self.base_url = "https://newsapi.org/v2"

    def fetch_top_tech_news(self, limit=3):
        url = f"{self.base_url}/top-headlines"
        params = {
            "category": "technology",
            "language": "en",
            "pageSize": limit,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=CONFIG["REQUEST_TIMEOUT"])
            response.raise_for_status()
            data = response.json()
            return data.get("articles", [])
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to fetch news. Details: {e}")
            return []

if __name__ == "__main__":
    fetcher = NewsFetcher()
    print("Fetching top tech news from News API...\n")
    articles = fetcher.fetch_top_tech_news()
    
    if not articles:
        print("No articles found or API call failed.")
    else:
        for idx, article in enumerate(articles, 1):
            print(f"{idx}. {article.get('title')}")
            print(f"   Source: {article.get('source', {}).get('name')}")
            print(f"   URL: {article.get('url')}\n")
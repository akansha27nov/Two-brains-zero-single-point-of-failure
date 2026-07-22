from news_api import NewsFetcher
from llm_providers import OpenAIProvider, CohereProvider
from budget_manager import TokenBudgetManager
from config import CONFIG

class NewsSummarizer:
    def __init__(self):
        self.budget_manager = TokenBudgetManager(daily_budget=CONFIG["DAILY_BUDGET"])
        self.fetcher = NewsFetcher()
        self.summarizer = OpenAIProvider(self.budget_manager)
        self.analyzer = CohereProvider(self.budget_manager)

    def process_news(self, limit=3):
        print(f"Fetching up to {limit} articles...")
        articles = self.fetcher.fetch_top_tech_news(limit=limit)
        results = []
        
        for idx, article in enumerate(articles, 1):
            title = article.get('title')
            content = article.get('description') or title
            print(f"\nProcessing [{idx}/{len(articles)}]: {title}")
            
            try:
                summary = self.summarizer.summarize(content)
                sentiment = self.analyzer.analyze_sentiment(summary)
            except Exception as e:
                print(f"Budget or Processing Error: {e}")
                break
            
            results.append({
                "title": title,
                "summary": summary,
                "sentiment": sentiment,
                "url": article.get("url")
            })
            
        return results
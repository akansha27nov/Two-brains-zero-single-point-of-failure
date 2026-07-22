# Core orchestration for news summarization and sentiment analysis.
# Provides sync and async pipelines for the same workflow.
# Uses shared budget tracking across providers.
import aiohttp
import asyncio
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

    # Run the current pipeline synchronously.
    def process_news(self, limit=3):
        print(f"Fetching up to {limit} articles (Sync)...")
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


class AsyncNewsSummarizer(NewsSummarizer):
    """Advanced asynchronous summarizer"""

    # Estimate the cost of processing one article before scheduling it.
    def _estimate_article_cost(self, text: str) -> float:
        """Conservatively estimate the OpenAI + Cohere cost for one article."""
        if not text:
            return 0.0

        # Rough input-token estimate for the summary prompt, plus a conservative
        # allowance for the 150-token OpenAI completion and the follow-up sentiment call.
        estimated_openai_input_tokens = len(text.split()) + 20
        estimated_openai_output_tokens = 150
        estimated_cohere_input_tokens = len(text.split()) + 40

        openai_cost = self.budget_manager.calculate_cost(
            "openai",
            "gpt-4o-mini",
            estimated_openai_input_tokens,
            estimated_openai_output_tokens,
        )
        cohere_cost = self.budget_manager.calculate_cost(
            "cohere",
            "command-r-08-2024",
            estimated_cohere_input_tokens,
            1,
        )
        return openai_cost + cohere_cost

    # Fetch headlines with aiohttp instead of the sync requests client.
    async def _fetch_news(self, session: aiohttp.ClientSession, limit: int):
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": "technology",
            "language": "en",
            "pageSize": str(limit),
            "apiKey": CONFIG["NEWS_API_KEY"]
        }
        async with session.get(url, params=params, timeout=CONFIG["REQUEST_TIMEOUT"]) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("articles", [])

    # Summarize one article through the OpenAI HTTP endpoint.
    async def _summarize_openai(self, session: aiohttp.ClientSession, text: str):
        if not text:
            return "No content."
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {CONFIG['OPENAI_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a concise news summarizer."},
                {"role": "user", "content": f"Summarize this in 2 sentences:\n{text}"}
            ],
            "max_tokens": 150
        }
        async with session.post(url, headers=headers, json=payload, timeout=CONFIG["REQUEST_TIMEOUT"]) as resp:
            resp.raise_for_status()
            data = await resp.json()
            summary = data["choices"][0]["message"]["content"].strip()
            
            usage = data.get("usage", {})
            self.budget_manager.track_request(
                "openai", "gpt-4o-mini", 
                usage.get("prompt_tokens", 0), 
                usage.get("completion_tokens", 0)
            )
            return summary

    # Classify the summary sentiment through the Cohere HTTP endpoint.
    async def _analyze_cohere(self, session: aiohttp.ClientSession, text: str):
        if not text:
            return "Neutral"
        url = "https://api.cohere.ai/v1/chat"
        headers = {
            "Authorization": f"Bearer {CONFIG['COHERE_API_KEY']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "model": "command-r-08-2024",
            "message": f"Analyze sentiment (Respond ONLY Positive, Negative, or Neutral):\n{text}"
        }
        async with session.post(url, headers=headers, json=payload, timeout=CONFIG["REQUEST_TIMEOUT"]) as resp:
            resp.raise_for_status()
            data = await resp.json()
            sentiment = data.get("text", "").strip()
            
            meta = data.get("meta", {})
            billed_units = meta.get("billed_units", {})
            self.budget_manager.track_request(
                "cohere", "command-r-08-2024", 
                billed_units.get("input_tokens", 0), 
                billed_units.get("output_tokens", 0)
            )
            return sentiment

    # Process a single article end to end.
    async def _process_single_article(self, session: aiohttp.ClientSession, article: dict, idx: int, total: int):
        title = article.get('title')
        content = article.get('description') or title
        print(f"\n[Async Worker] Processing [{idx}/{total}]: {title}")
        
        try:
            summary = await self._summarize_openai(session, content)
            sentiment = await self._analyze_cohere(session, summary)
        except Exception as e:
            print(f"Error processing article {idx} via aiohttp: {e}")
            return None
        
        return {
            "title": title,
            "summary": summary,
            "sentiment": sentiment,
            "url": article.get("url")
        }

    # Fetch headlines, reserve budget, and fan out accepted articles concurrently.
    async def process_news_async(self, limit=3):
        print(f"Fetching up to {limit} articles asynchronously using pure aiohttp...")
        
        async with aiohttp.ClientSession() as session:
            try:
                articles = await self._fetch_news(session, limit)
            except Exception as e:
                print(f"ERROR: Failed to fetch news via aiohttp: {e}")
                return []
            
            if not articles:
                print("[-] No articles found.")
                return []
                
            tasks = []
            reserved_budget = 0.0
            for idx, article in enumerate(articles, 1):
                title = article.get("title")
                content = article.get("description") or title or ""
                estimated_cost = self._estimate_article_cost(content)
                remaining_budget = self.budget_manager.daily_budget - self.budget_manager.used_budget - reserved_budget

                if estimated_cost > remaining_budget:
                    print("WARNING: Daily budget would be exceeded. Stopping async scheduling.")
                    break

                reserved_budget += estimated_cost
                tasks.append(self._process_single_article(session, article, idx, len(articles)))
            
            results = await asyncio.gather(*tasks)
            return [res for res in results if res is not None]

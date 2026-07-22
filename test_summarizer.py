import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from config import CONFIG
from database import NewsDatabase
from news_api import NewsFetcher
from llm_providers import OpenAIProvider, CohereProvider
from budget_manager import TokenBudgetManager
from summarizer import NewsSummarizer, AsyncNewsSummarizer


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture
def in_memory_db(tmp_path):
    """Fixture providing an isolated SQLite database file per test run."""
    db_file = tmp_path / "test_cache.db"
    return NewsDatabase(db_path=str(db_file))


@pytest.fixture
def mock_news_articles():
    return [
        {
            "title": "Test AI Article",
            "description": "An article about testing AI pipelines.",
            "url": "https://example.com/test-ai"
        }
    ]


# =====================================================================
# 1. CONFIG & PROVIDER FALLBACK TESTS (ORIGINAL TESTS)
# =====================================================================

def test_config_keys_present():
    """Ensure essential configuration keys exist."""
    assert "OPENAI_API_KEY" in CONFIG
    assert "COHERE_API_KEY" in CONFIG
    assert "NEWS_API_KEY" in CONFIG
    assert "DAILY_BUDGET" in CONFIG


def test_openai_fallback_on_exception():
    """Verify OpenAIProvider returns fallback text when an exception occurs."""
    budget_mgr = TokenBudgetManager(daily_budget=5.0)
    
    with patch("llm_providers.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Unavailable")
        mock_openai_cls.return_value = mock_client
        
        provider = OpenAIProvider(budget_mgr)
        result = provider.summarize("Test article text")
        
        assert "Fallback activated" in result


def test_cohere_fallback_on_exception():
    """Verify CohereProvider returns fallback sentiment when an exception occurs."""
    budget_mgr = TokenBudgetManager(daily_budget=5.0)
    
    with patch("llm_providers.cohere.Client") as mock_cohere_cls:
        mock_client = MagicMock()
        mock_client.chat.side_effect = Exception("Service Down")
        mock_cohere_cls.return_value = mock_client
        
        provider = CohereProvider(budget_mgr)
        result = provider.analyze_sentiment("Test summary text")
        
        assert "Neutral" in result or "Fallback" in result


# =====================================================================
# 2. BUDGET MANAGER TESTS (ORIGINAL TESTS)
# =====================================================================

def test_budget_tracking_accumulates():
    """Verify budget manager correctly tracks cost accumulation."""
    manager = TokenBudgetManager(daily_budget=5.0)
    
    # Track 1,000 input & output tokens for OpenAI gpt-4o-mini
    manager.track_request("openai", "gpt-4o-mini", 1000, 1000)
    
    assert manager.used_budget > 0.0
    assert manager.used_budget < manager.daily_budget


def test_budget_exceeded_raises_exception():
    """Verify budget manager raises an exception when budget is exceeded."""
    manager = TokenBudgetManager(daily_budget=0.00001)
    
    with pytest.raises(Exception) as exc_info:
        # Requesting tokens that exceed tiny budget
        manager.track_request("openai", "gpt-4o-mini", 5000, 5000)
    
    assert "Token budget exceeded" in str(exc_info.value)


# =====================================================================
# 3. SYNC PIPELINE & DATABASE CACHING TESTS (NEW TESTS)
# =====================================================================

def test_sync_cache_miss_and_save(in_memory_db, mock_news_articles):
    """Verify fresh articles are fetched, processed, and saved to DB."""
    with patch("summarizer.NewsFetcher.fetch_top_tech_news", return_value=mock_news_articles), \
         patch("summarizer.OpenAIProvider.summarize", return_value="Summary text"), \
         patch("summarizer.CohereProvider.analyze_sentiment", return_value="Positive"):
        
        summarizer = NewsSummarizer()
        summarizer.db = in_memory_db
        
        results = summarizer.process_news(limit=1)
        
        assert len(results) == 1
        assert results[0]["title"] == "Test AI Article"
        assert results[0]["summary"] == "Summary text"
        assert results[0]["sentiment"] == "Positive"
        
        # Verify it was saved to SQLite
        cached = in_memory_db.get_cached_article("https://example.com/test-ai")
        assert cached is not None
        assert cached["summary"] == "Summary text"


def test_sync_cache_hit_bypasses_llm(in_memory_db, mock_news_articles):
    """Verify cached articles bypass OpenAI/Cohere API calls completely."""
    # Pre-populate DB
    in_memory_db.save_article({
        "url": "https://example.com/test-ai",
        "title": "Test AI Article",
        "summary": "Cached Summary",
        "sentiment": "Neutral"
    })
    
    mock_openai = MagicMock()
    mock_cohere = MagicMock()

    with patch("summarizer.NewsFetcher.fetch_top_tech_news", return_value=mock_news_articles):
        summarizer = NewsSummarizer()
        summarizer.db = in_memory_db
        summarizer.summarizer.summarize = mock_openai
        summarizer.analyzer.analyze_sentiment = mock_cohere
        
        results = summarizer.process_news(limit=1)
        
        # Verify result came from cache
        assert len(results) == 1
        assert results[0]["summary"] == "Cached Summary"
        
        # Verify LLM providers were NEVER called
        mock_openai.assert_not_called()
        mock_cohere.assert_not_called()


# =====================================================================
# 4. ASYNC PIPELINE CACHING TEST (FIXED FOR PLAIN PYTEST)
# =====================================================================

def test_async_process_cached_article(in_memory_db, mock_news_articles):
    """Verify AsyncNewsSummarizer respects cache without needing pytest-asyncio plugin."""
    
    async def run_test():
        # Pre-populate DB
        in_memory_db.save_article({
            "url": "https://example.com/test-ai",
            "title": "Test AI Article",
            "summary": "Async Cached Summary",
            "sentiment": "Positive"
        })

        async_summarizer = AsyncNewsSummarizer()
        async_summarizer.db = in_memory_db

        # Mock _fetch_news to return test article
        async_summarizer._fetch_news = AsyncMock(return_value=mock_news_articles)
        async_summarizer._summarize_openai = AsyncMock()
        async_summarizer._analyze_cohere = AsyncMock()

        results = await async_summarizer.process_news_async(limit=1)

        assert len(results) == 1
        assert results[0]["summary"] == "Async Cached Summary"
        
        # Verify network/LLM requests were skipped
        async_summarizer._summarize_openai.assert_not_called()
        async_summarizer._analyze_cohere.assert_not_called()

    # Execute async test function cleanly via asyncio.run
    asyncio.run(run_test())
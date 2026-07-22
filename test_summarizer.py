import pytest
from unittest.mock import MagicMock, patch

from news_api import NewsFetcher
from llm_providers import OpenAIProvider, CohereProvider
from summarizer import NewsSummarizer
from budget_manager import TokenBudgetManager
from config import CONFIG


@pytest.fixture
def sample_articles():
    """Sample article data mimicking NewsFetcher output."""
    return [
        {
            "title": "Test Article One",
            "description": "A description of test article one.",
            "url": "https://example.com/1",
        },
        {
            "title": "Test Article Two",
            "description": "A description of test article two.",
            "url": "https://example.com/2",
        },
    ]


class TestNewsSummarizerPipeline:
    """Tests for the main orchestrator."""

    @patch.object(NewsFetcher, "fetch_top_tech_news")
    @patch.object(OpenAIProvider, "summarize")
    @patch.object(CohereProvider, "analyze_sentiment")
    def test_process_news_success(self, mock_sentiment, mock_summary, mock_fetch, sample_articles):
        mock_fetch.return_value = sample_articles
        mock_summary.return_value = "A concise summary."
        mock_sentiment.return_value = "Positive"

        summarizer = NewsSummarizer()
        results = summarizer.process_news(limit=2)

        assert len(results) == 2
        assert results[0]["title"] == "Test Article One"
        assert results[0]["summary"] == "A concise summary."
        assert results[0]["sentiment"] == "Positive"

    @patch.object(NewsFetcher, "fetch_top_tech_news")
    def test_empty_articles_list(self, mock_fetch):
        mock_fetch.return_value = []

        summarizer = NewsSummarizer()
        results = summarizer.process_news(limit=2)

        assert results == []


class TestLLMProvidersFallback:
    """Tests verifying fallback strings when APIs fail."""

    @patch("llm_providers.OpenAI")
    def test_openai_fallback_on_exception(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("OpenAI Outage")

        provider = OpenAIProvider()
        result = provider.summarize("Sample text")

        assert "Fallback activated" in result

    @patch("llm_providers.cohere.Client")
    def test_cohere_fallback_on_exception(self, mock_cohere_class):
        mock_client = MagicMock()
        mock_cohere_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("Cohere Outage")

        provider = CohereProvider()
        result = provider.analyze_sentiment("Sample text")

        assert "Fallback activated" in result


class TestTokenBudgetManager:
    """Tests for budget tracking and enforcement."""

    def test_budget_tracking_accumulates(self):
        budget = TokenBudgetManager(daily_budget=5.00)
        
        # 10,000 input and output tokens on gpt-4o-mini
        budget.track_request("openai", "gpt-4o-mini", 10000, 10000)
        
        assert budget.used_budget > 0
        assert budget.provider_usage["openai"]["input_tokens"] == 10000

    def test_budget_exceeded_raises_exception(self):
        budget = TokenBudgetManager(daily_budget=0.0001)  # Ultra small budget

        with pytest.raises(Exception) as exc_info:
            budget.track_request("openai", "gpt-4o-mini", 100000, 100000)

        assert "Token budget exceeded" in str(exc_info.value)
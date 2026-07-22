# Lab Proof & Verification Evidence

## 1. Automated Test Suite Execution
All unit tests—covering configuration validation, mock HTTP requests, LLM fallback recovery, and budget enforcement—pass successfully.

**Note:** below output is without cache implementation

```
$ pytest test_summarizer.py -v

======================================== test session starts =========================================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /opt/anaconda3/envs/bootcamp-env/bin/python3.11
cachedir: .pytest_cache
rootdir: /Users/akanshaverma/Projects/AC-bootcamp/week 3/Two-brains-zero-single-point-of-failure
plugins: anyio-4.14.2, langsmith-0.10.6
collected 6 items                                                                                    

test_summarizer.py::TestNewsSummarizerPipeline::test_process_news_success PASSED               [ 16%]
test_summarizer.py::TestNewsSummarizerPipeline::test_empty_articles_list PASSED                [ 33%]
test_summarizer.py::TestLLMProvidersFallback::test_openai_fallback_on_exception PASSED         [ 50%]
test_summarizer.py::TestLLMProvidersFallback::test_cohere_fallback_on_exception PASSED         [ 66%]
test_summarizer.py::TestTokenBudgetManager::test_budget_tracking_accumulates PASSED            [ 83%]
test_summarizer.py::TestTokenBudgetManager::test_budget_exceeded_raises_exception PASSED       [100%]

========================================= 6 passed in 0.24s ==========================================
```
## 2. Output of tests with cache implementation

```
=============================================== test session starts ================================================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0 -- /opt/anaconda3/envs/bootcamp-env/bin/python3.11
cachedir: .pytest_cache
rootdir: /Users/akanshaverma/Projects/AC-bootcamp/week 3/Two-brains-zero-single-point-of-failure
plugins: anyio-4.14.2, langsmith-0.10.6
collected 8 items                                                                                                  

test_summarizer.py::test_config_keys_present PASSED                                                          [ 12%]
test_summarizer.py::test_openai_fallback_on_exception PASSED                                                 [ 25%]
test_summarizer.py::test_cohere_fallback_on_exception PASSED                                                 [ 37%]
test_summarizer.py::test_budget_tracking_accumulates PASSED                                                  [ 50%]
test_summarizer.py::test_budget_exceeded_raises_exception PASSED                                             [ 62%]
test_summarizer.py::test_sync_cache_miss_and_save PASSED                                                     [ 75%]
test_summarizer.py::test_sync_cache_hit_bypasses_llm PASSED                                                  [ 87%]
test_summarizer.py::test_async_process_cached_article PASSED                                                 [100%]

================================================ 8 passed in 0.41s =================================================
```
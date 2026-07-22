# Multi-Provider News Summarizer & Sentiment Analyzer

This system fetches current technology headlines, summarizes them using OpenAI, analyzes sentiment using Cohere, and manages financial safety constraints using a custom token budget manager.

---

## What this Project does

* **Flexible News Fetching:** Pulls top headlines from NewsAPI by tech category.
* **Multi-Model Intelligence:** Summarizes each article using OpenAI (`gpt-4o-mini`) and analyzes sentiment using Cohere (`command-r-08-2024`).
* **Resilient Fallbacks:** Falls back gracefully if an external API provider fails, ensuring continuous execution without crashing.
* **Active Cost Tracking:** Tracks and reports precise API costs per run based on exact token usage with active daily budget guardrails.
* **Local Caching & Resilient Storage:** Caches processed articles in SQLite to eliminate double-billing, with automatic fallback to system temporary directories in read-only environments.

## Key Features

* **Granular Token Tracking:** Tracks exact input and output token usage directly from API responses with real-time per-1M token cost calculations.
* **Active Budget Enforcement:** Automatically raises exceptions and halts execution if API expenditures breach the configured `DAILY_BUDGET`.
* **High-Performance Async Pipeline:** Implements asynchronous HTTP request handling using `aiohttp` alongside proactive cost pre-estimation for concurrent article processing.
* **Robust Error Handling & Fallbacks:** Gracefully handles provider outages and network anomalies via fallback strings and mocked test units.
---

## Project Structure

```text
├── .env                  # Environment variables (API keys & configuration)
├── requirements.txt      # Project dependencies
├── config.py             # Configuration loader and environment validator
├── budget_manager.py     # Token budget tracking and cost calculation
├── news_api.py           # Sync and async news fetchers
├── llm_providers.py      # OpenAI and Cohere client wrappers
├── summarizer.py         # Sync orchestrator and AsyncNewsSummarizer (aiohttp)
├── main.py               # Application entry point
└── test_summarizer.py    # Pytest unit test suite
```

## Installation & Setup

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Configure your environment variables
Take a look at `.env.example` and create a .env file in the root directory.

## Running the Application
```bash
python main.py
```

## Running Tests
Execute the automated test suite with pytest:

```bash
pytest test_summarizer.py -v
```
## Example Output

```bash
============================================================
      MULTI-PROVIDER NEWS SUMMARIZER & SENTIMENT ANALYZER   
============================================================
How many articles would you like to process? (Default 3): 

[+] Initializing pipeline...
Fetching up to 3 articles (Sync)...

Processing [1/3]: The New Mercedes-Maybach GLS Debuts With More Power, Better Style - Motor1.com

Processing [2/3]: iOS 27 beta 4 adds a useful Apple TV app feature, here’s how it works - 9to5Mac

Processing [3/3]: A mathematician used Fable 5 to disprove a major math problem - Mashable

============================================================
                   SUMMARY & ANALYSIS REPORT                
============================================================

[1] The New Mercedes-Maybach GLS Debuts With More Power, Better Style - Motor1.com
    URL:       https://www.motor1.com/news/802238/2027-mercedes-maybach-gls-680-engine-specs-details/
    Summary:   Mercedes-Benz has introduced the 2027 Maybach GLS 680, featuring a more powerful twin-turbocharged V8 engine along with a refreshed design. The new model aims to enhance performance and luxury for its high-end clientele.
    Sentiment: Positive.
------------------------------------------------------------

[2] iOS 27 beta 4 adds a useful Apple TV app feature, here’s how it works - 9to5Mac
    URL:       https://9to5mac.com/2026/07/20/ios-27-beta-4-adds-a-useful-apple-tv-app-feature-heres-how-it-works/
    Summary:   Apple has released iOS 27 beta 4, introducing a new “Automatic Downloads” feature to enhance user experience. This update aims to streamline app updates by automatically downloading them as they become available.
    Sentiment: Positive.
------------------------------------------------------------

[3] A mathematician used Fable 5 to disprove a major math problem - Mashable
    URL:       https://mashable.com/tech/anthropic-fable-5-disproves-jacobian-conjecture
    Summary:   The Jacobian conjecture has posed a significant challenge to mathematicians for almost 90 years. It remains an unresolved problem in the field of algebraic geometry, attracting ongoing interest and research.
    Sentiment: Neutral.
------------------------------------------------------------

============================================================
TOKEN BUDGET SUMMARY
============================================================
Daily Budget: $5.00
Used: $0.00010 (0.00%)
Remaining: $4.99990

Provider Breakdown:
  OPENAI:
    Input tokens:  165
    Output tokens: 124
    Total cost:    $0.00010
  COHERE:
    Input tokens:  168.0
    Output tokens: 6.0
    Total cost:    $0.00000
============================================================
```

## Cost Analysis
The system enforces strict financial guardrails via the `TokenBudgetManager`:

- **Exact Pricing Tiers:** Costs are calculated dynamically using real-world pricing models (e.g., OpenAI gpt-4o-mini at $0.150 / 1M input tokens and $0.600 / 1M output tokens).

- **Precise Extraction:** Rather than estimating text length, token counts are parsed directly from vendor response metadata (usage and meta fields).

- **Active Guardrails:** If projected or cumulative spend exceeds the configured DAILY_BUDGET, the application blocks execution to prevent runaway cloud bills.

## Optional Stretches implemented

1. Add response caching to avoid re-processing identical articles
2. Store processed articles in SQLite database

```
============================================================
      MULTI-PROVIDER NEWS SUMMARIZER & SENTIMENT ANALYZER   
============================================================
How many articles would you like to process? (Default 3): 

[+] Initializing pipeline...
Fetching up to 3 articles (Sync)...

Processing [1/3]: The New Mercedes-Maybach GLS Debuts With More Power, Better Style - Motor1.com
[Cache Hit] Skipping API call for: The New Mercedes-Maybach GLS Debuts With More Power, Better Style - Motor1.com

Processing [2/3]: iOS 27 beta 4 adds a useful Apple TV app feature, here’s how it works - 9to5Mac
[Cache Hit] Skipping API call for: iOS 27 beta 4 adds a useful Apple TV app feature, here’s how it works - 9to5Mac

Processing [3/3]: A $33,700 Tiny Home That Finally Gets the Floor Plan Right - Yanko Design
[Cache Hit] Skipping API call for: A $33,700 Tiny Home That Finally Gets the Floor Plan Right - Yanko Design

============================================================
                   SUMMARY & ANALYSIS REPORT                
============================================================

[1] The New Mercedes-Maybach GLS Debuts With More Power, Better Style - Motor1.com
    URL:       https://www.motor1.com/news/802238/2027-mercedes-maybach-gls-680-engine-specs-details/
    Summary:   Mercedes-Benz has introduced the 2027 Maybach GLS 680, featuring a more powerful twin-turbocharged V8 engine and a refreshed design. The updates enhance both performance and aesthetics for this luxury SUV.
    Sentiment: Positive.
------------------------------------------------------------

[2] iOS 27 beta 4 adds a useful Apple TV app feature, here’s how it works - 9to5Mac
    URL:       https://9to5mac.com/2026/07/20/ios-27-beta-4-adds-a-useful-apple-tv-app-feature-heres-how-it-works/
    Summary:   Apple has released iOS 27 beta 4, introducing a new "Automatic Downloads" feature that enhances user experience. This update aims to streamline the process of app and content downloads on Apple devices.
    Sentiment: Positive.
------------------------------------------------------------

[3] A $33,700 Tiny Home That Finally Gets the Floor Plan Right - Yanko Design
    URL:       https://www.yankodesign.com/2026/07/20/a-33700-tiny-home-that-finally-gets-the-floor-plan-right/
    Summary:   The tiny home movement continues to thrive and surprise, as evidenced by innovative projects like the Fairfax 20. Each new development challenges the notion that the trend has peaked, highlighting its ongoing evolution and appeal.
    Sentiment: Positive.
------------------------------------------------------------

============================================================
TOKEN BUDGET SUMMARY
============================================================
Daily Budget: $5.00
Used: $0.00000 (0.00%)
Remaining: $5.00000

Provider Breakdown:
============================================================
```

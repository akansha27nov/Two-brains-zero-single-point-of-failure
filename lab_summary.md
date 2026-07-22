# Lab Summary

**Integrating multiple LLM providers (`OpenAI` for summarization and `Cohere` for sentiment analysis)**

This laboratory exercise focused on building a robust, production-ready AI application that avoids single points of failure by integrating multiple language model providers. Beyond basic orchestration, the system implements rigorous token budget controls, asynchronous performance optimization with `aiohttp`, local SQLite database caching, and a comprehensive unit-testing harness.

One of the primary challenges encountered during this lab was resolving initialization errors when mocking top-level client constructors during unit testing, which was successfully solved by shifting mock assertions to target client instance behaviors instead of class instantiation. Additionally, integrating SQLite caching resolved the issue of redundant API processing, preventing double-billing on identical news articles.

Through this exercise, I learned how to effectively decouple multi-provider architectures, implement granular cost controls, persist LLM outputs locally, and ensure system resilience against third-party API outages. 

For future improvements, creating a Web UI (using FastAPI or Streamlit) and supporting free-text keyword search parameters for NewsAPI queries would further enhance usability and flexibility.
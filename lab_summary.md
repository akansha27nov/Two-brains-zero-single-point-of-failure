# Lab Summary

**Integrating multiple LLM providers (`OpenAI` for summarization and `Cohere` for sentiment analysis)**

This laboratory exercise focused on building a robust, production-ready AI application that avoids single points of failure by integrating multiple language model providers. Beyond basic orchestration, the system implements rigorous token budget controls, asynchronous performance optimization with `aiohttp`, and a comprehensive unit-testing harness.

One of the primary challenges encountered during this lab was resolving initialization errors when mocking top-level client constructors during unit testing, which was successfully solved by shifting mock assertions to target client instance behaviors instead of class instantiation. 

Through this exercise, I learned how to effectively decouple multi-provider architectures, implement granular cost controls, and ensure system resilience against third-party API outages. 

For future improvements, adding a local caching layer (such as SQLite) and supporting full text-query search parameters for the NewsAPI would further enhance performance and flexibility.
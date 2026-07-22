"""
CLI entry point for the news summarizer. Prompts for how many articles to process.
Prints the final report and budget summary
Author: Akansha Verma
"""

import sys
from summarizer import NewsSummarizer

# Run the synchronous pipeline from the command line.
def run_app():
    print("=" * 60)
    print("      MULTI-PROVIDER NEWS SUMMARIZER & SENTIMENT ANALYZER   ")
    print("=" * 60)
    
    try:
        limit_input = input("How many articles would you like to process? (Default 3): ").strip()
        limit = int(limit_input) if limit_input.isdigit() else 3
    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit(0)

    print(f"\n[+] Initializing pipeline...")
    
    app = NewsSummarizer()
    results = app.process_news(limit=limit)

    if not results:
        print("[-] No articles processed.")
        return

    print("\n" + "=" * 60)
    print("                   SUMMARY & ANALYSIS REPORT                ")
    print("=" * 60)

    for idx, item in enumerate(results, 1):
        print(f"\n[{idx}] {item['title']}")
        print(f"    URL:       {item['url']}")
        print(f"    Summary:   {item['summary']}")
        print(f"    Sentiment: {item['sentiment']}")
        print("-" * 60)

    app.budget_manager.print_summary()

if __name__ == "__main__":
    run_app()

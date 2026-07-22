# Central configuration loader for API keys and runtime limits.
# Reads environment variables once at import time.
# Provides a small validation helper for required keys.
import os
import sys
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "COHERE_API_KEY": os.getenv("COHERE_API_KEY"),
    "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
    "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
    "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "30")),
    "DAILY_BUDGET": float(os.getenv("DAILY_BUDGET", "5.00"))
}

# Validate that required API keys are present before running the app.
def validate_config():
    missing_keys = [k for k, v in CONFIG.items() if not v and "KEY" in k]
    if missing_keys:
        print(f"CRITICAL ERROR: Missing configuration keys: {', '.join(missing_keys)}")
        sys.exit(1)
    print("SUCCESS: Configuration validated successfully.")

if __name__ == "__main__":
    validate_config()

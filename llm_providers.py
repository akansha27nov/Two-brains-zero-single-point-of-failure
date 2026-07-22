# Provider wrappers for OpenAI and Cohere.
# Centralizes API calls, prompt formatting, and budget tracking.
# Keeps fallback behavior in one place.
from config import CONFIG
from openai import OpenAI
import cohere
from budget_manager import TokenBudgetManager

class OpenAIProvider:
    # Set up the OpenAI client and shared budget manager.
    def __init__(self, budget_manager: TokenBudgetManager = None):
        self.client = OpenAI(api_key=CONFIG["OPENAI_API_KEY"])
        self.model = "gpt-4o-mini"
        self.budget_manager = budget_manager

    # Generate a short summary from article text.
    def summarize(self, text):
        if not text:
            return "No content to summarize."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a concise news summarizer."},
                    {"role": "user", "content": f"Summarize this in 2 sentences:\n{text}"}
                ],
                max_tokens=150
            )
            summary = response.choices[0].message.content.strip()
            
            if self.budget_manager:
                i_toks = response.usage.prompt_tokens
                o_toks = response.usage.completion_tokens
                self.budget_manager.track_request("openai", self.model, i_toks, o_toks)
                
            return summary
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "Summarization failed (Fallback activated)."

class CohereProvider:
    # Set up the Cohere client and shared budget manager.
    def __init__(self, budget_manager: TokenBudgetManager = None):
        self.client = cohere.Client(api_key=CONFIG["COHERE_API_KEY"])
        self.model = "command-r-08-2024"
        self.budget_manager = budget_manager

    # Classify text sentiment with Cohere.
    def analyze_sentiment(self, text):
        if not text:
            return "Neutral"
        try:
            response = self.client.chat(
                message=f"Analyze sentiment (Respond ONLY Positive, Negative, or Neutral):\n{text}",
                model=self.model
            )
            sentiment = response.text.strip()
            
            if self.budget_manager and hasattr(response, 'meta') and response.meta.billed_units:
                i_toks = response.meta.billed_units.input_tokens or 0
                o_toks = response.meta.billed_units.output_tokens or 0
                self.budget_manager.track_request("cohere", self.model, i_toks, o_toks)
                
            return sentiment
        except Exception as e:
            print(f"Cohere Error: {e}")
            return "Sentiment Analysis Failed (Fallback activated)."

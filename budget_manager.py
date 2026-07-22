from typing import Dict, Any

class TokenBudgetManager:
    """Manage token budgets using direct API usage data."""
    
    def __init__(self, daily_budget: float = 5.00):
        self.daily_budget = daily_budget
        self.used_budget = 0.0
        self.provider_usage = {
            "openai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0},
            "cohere": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        }
        
        self.pricing = {
            "openai": {
                "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000}
            },
            "cohere": {
                "command-r-08-2024": {"input": 0.00, "output": 0.00} # Free trial!
            }
        }
    
    def calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        if provider not in self.pricing or model not in self.pricing[provider]:
            return 0.0
        
        pricing = self.pricing[provider][model]
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        return input_cost + output_cost
    
    def track_request(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        
        if self.used_budget + cost > self.daily_budget:
            remaining = self.daily_budget - self.used_budget
            raise Exception(f"Token budget exceeded! Request cost ${cost:.6f}, only ${remaining:.6f} remaining.")
        
        self.used_budget += cost
        if provider in self.provider_usage:
            self.provider_usage[provider]["input_tokens"] += input_tokens
            self.provider_usage[provider]["output_tokens"] += output_tokens
            self.provider_usage[provider]["cost"] += cost
        
        return {"cost": cost, "remaining_budget": self.daily_budget - self.used_budget}
    
    def print_summary(self):
        print("\n" + "=" * 60)
        print("TOKEN BUDGET SUMMARY")
        print("=" * 60)
        print(f"Daily Budget: ${self.daily_budget:.2f}")
        percent_used = (self.used_budget / self.daily_budget) * 100
        print(f"Used: ${self.used_budget:.5f} ({percent_used:.2f}%)")
        print(f"Remaining: ${(self.daily_budget - self.used_budget):.5f}")
        print("\nProvider Breakdown:")
        for provider, usage in self.provider_usage.items():
            if usage['input_tokens'] > 0 or usage['output_tokens'] > 0:
                print(f"  {provider.upper()}:")
                print(f"    Input tokens:  {usage['input_tokens']:,}")
                print(f"    Output tokens: {usage['output_tokens']:,}")
                print(f"    Total cost:    ${usage['cost']:.5f}")
        print("=" * 60)
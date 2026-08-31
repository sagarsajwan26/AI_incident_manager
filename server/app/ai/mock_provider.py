from app.ai.base import LLMProvider


class MockLLMProvider(LLMProvider):
    async def generate(self, prompt) -> str:

        return """
      {
            "summary": "The production API is experiencing failures.",
            "likely_root_cause": "Database connection timeout.",
            "evidence": [
                "ERROR database connection timeout after 30 seconds"
            ],
            "impact": "Production API requests may fail.",
            "recommended_actions": [
                "Check database availability.",
                "Inspect database connection pool usage.",
                "Review recent deployments."
            ],
            "confidence": 0.85
        }
        """

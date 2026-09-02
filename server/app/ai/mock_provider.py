from app.ai.base import LLMProvider


class MockLLMProvider(LLMProvider):

    async def generate(self, prompt: str) -> str:
        return """
        {
            "summary": "The incident includes a database connection timeout, but the supplied evidence does not establish the root cause.",
            "likely_root_cause": "Insufficient evidence to determine root cause.",
            "root_cause_status": "unknown",
            "evidence": [
                "ERROR database connection timeout after 30 seconds"
            ],
            "evidence_assessment": [
                {
                    "claim": "A database connection timeout occurred after 30 seconds.",
                    "support": "The supplied evidence explicitly contains the timeout error.",
                    "is_direct": true,
                    "supports_root_cause": false
                },
                {
                    "claim": "The database timeout caused the testing deletion.",
                    "support": "The supplied evidence does not establish this causal relationship.",
                    "is_direct": false,
                    "supports_root_cause": false
                }
            ],
            "impact": "The affected system may experience failed requests.",
            "recommended_actions": [
                "Review application logs.",
                "Review database activity.",
                "Review deployment history."
            ],
            "unknowns": [
                "Whether the database timeout caused the testing deletion.",
                "What event actually caused the deletion."
            ],
            "confidence": 0.4
        }
        """

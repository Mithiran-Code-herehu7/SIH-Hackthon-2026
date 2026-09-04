from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):

    def generate(
        self,
        prompt: str,
    ) -> str:
        return (
            "Based on the provided document, "
            "the refinery uses crude oil distillation units "
            "for crude oil processing. The distillation process "
            "separates crude oil into different fractions "
            "based on their boiling points."
        )
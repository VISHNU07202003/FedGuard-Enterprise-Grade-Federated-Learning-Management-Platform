from .base import LLMClient

class MockLLMClient(LLMClient):
    async def generate(self, prompt: str, context: dict | None = None) -> str:
        return f"[MOCK RESPONSE] Acknowledging prompt: '{prompt[:50]}...' Context: {bool(context)}"

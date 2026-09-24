from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: dict | None = None) -> str:
        pass

from abc import ABC, abstractmethod
from typing import Optional

class LLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> dict:
        """
        Generate a response from the language model.
        Returns a dict containing 'answer', 'mode', and optionally 'warnings'.
        """
        pass

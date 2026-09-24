from typing import List, Dict, Any
from app.ai.llm_client import LLMClient
from app.core.secrets import get_secret
from app.core.config import settings

class OpenAILLMClient(LLMClient):
    def __init__(self):
        try:
            import openai
        except ImportError:
            raise ImportError("The 'openai' library is required to use the OpenAI LLM provider.")
            
        api_key = get_secret("LLM_API_KEY")
        
        # Support custom base URLs for proxies like LiteLLM
        base_url = None
        try:
            base_url = get_secret("LLM_API_BASE")
        except ValueError:
            pass
            
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        
        # Use Bedrock model ID field or fallback to mistral as a default model name
        self.model = settings.AWS_BEDROCK_MODEL_ID or "mistral"

    async def generate(self, messages: List[Dict[str, str]], system_prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
            
        formatted_messages.extend(messages)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "answer": response.choices[0].message.content,
                "mode": "openai",
                "warnings": []
            }
        except Exception as e:
            return {
                "answer": f"Error communicating with OpenAI/LiteLLM provider: {str(e)}",
                "mode": "openai",
                "warnings": [f"API Error: {str(e)}"]
            }

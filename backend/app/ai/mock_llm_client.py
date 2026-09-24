import json
from typing import Optional
from app.ai.llm_client import LLMClient

class MockLLMClient(LLMClient):
    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> dict:
        """
        Mock response for local development.
        Extracts context if possible to simulate grounding.
        """
        # Find context in the latest user message
        context_str = ""
        user_message = messages[-1].get("content", "")
        if "Context:" in user_message:
            parts = user_message.split("Context:", 1)
            context_str = parts[1].strip()
        
        answer = f"[MOCK MODE] I am FedGuard Copilot running locally.\n\n"
        if context_str:
            answer += "Based on the provided context, I can confirm this is a valid federated learning scenario. "
            if "dp_enabled" in context_str:
                answer += "Differential privacy is active, mitigating data exposure risks. "
            if "dropout_rate" in context_str:
                answer += "Some clients dropped out, which is typical in unpredictable environments. "
            if "anomaly" in context_str.lower():
                answer += "Anomaly detection metrics indicate potential issues with client contributions. "
            answer += "\n\n(This is a safe fallback response. Connect AWS Bedrock to generate dynamic AI insights.)"
        else:
            answer += "Please provide a specific run, experiment, or security event ID to retrieve insights."

        return {
            "answer": answer,
            "mode": "mock",
            "warnings": ["Using MockLLMClient. Bedrock is not configured."]
        }

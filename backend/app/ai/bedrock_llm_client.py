import logging
from typing import Optional
from app.ai.llm_client import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class BedrockLLMClient(LLMClient):
    def __init__(self):
        self._client = None
        self.model_id = settings.AWS_BEDROCK_MODEL_ID or "anthropic.claude-3-haiku-20240307-v1:0"
        self.region = settings.AWS_REGION or "us-east-1"
        self.guardrail_id = settings.AWS_BEDROCK_GUARDRAIL_ID
        self.guardrail_version = settings.AWS_BEDROCK_GUARDRAIL_VERSION

    def _get_client(self):
        import boto3
        if self._client is None:
            self._client = boto3.client("bedrock-runtime", region_name=self.region)
        return self._client

    async def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> dict:
        client = self._get_client()

        # Format messages for Bedrock Converse API
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })

        system_prompts = []
        if system_prompt:
            system_prompts.append({"text": system_prompt})

        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
        }

        # Optional Guardrail integration
        kwargs = {}
        if settings.COPILOT_ENABLE_GUARDRAILS and self.guardrail_id and self.guardrail_version:
            kwargs["guardrailConfig"] = {
                "guardrailIdentifier": self.guardrail_id,
                "guardrailVersion": self.guardrail_version,
                "trace": "DISABLED"
            }

        try:
            # We run the synchronous boto3 call in a thread pool via asyncio if we wanted to be perfectly async, 
            # but for this portfolio prototype, direct call is fine or we can wrap it. Let's wrap it nicely.
            import asyncio
            loop = asyncio.get_running_loop()
            
            def _invoke():
                return client.converse(
                    modelId=self.model_id,
                    messages=formatted_messages,
                    system=system_prompts,
                    inferenceConfig=inference_config,
                    **kwargs
                )

            response = await loop.run_in_executor(None, _invoke)
            
            output_message = response['output']['message']['content'][0]['text']
            
            return {
                "answer": output_message,
                "mode": "bedrock",
            }
        except Exception as e:
            logger.error(f"Bedrock generation failed: {e}")
            raise e

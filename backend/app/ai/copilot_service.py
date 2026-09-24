from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.ai.prompts import COPILOT_SYSTEM_PROMPT
from app.ai.guardrails import check_local_guardrails
from app.ai.rag_service import get_relevant_documentation
from app.ai.context_builder import build_context
from app.core.config import settings

def get_llm_client():
    provider = settings.LLM_PROVIDER.lower()
    if provider == "bedrock":
        from app.ai.bedrock_llm_client import BedrockLLMClient
        return BedrockLLMClient()
    elif provider == "openai" or provider == "litellm":
        from app.ai.openai_llm_client import OpenAILLMClient
        return OpenAILLMClient()
    else:
        from app.ai.mock_llm_client import MockLLMClient
        return MockLLMClient()

async def process_chat(db: AsyncSession, request: CopilotRequest) -> CopilotResponse:
    # 1. Local Guardrail Check
    block_reason = check_local_guardrails(request.message)
    if block_reason:
        return CopilotResponse(
            answer=block_reason,
            mode="mock" if settings.LLM_PROVIDER.lower() != "bedrock" else "bedrock",
            grounded=False,
            warnings=["Blocked by local guardrails."],
            created_at=datetime.now(timezone.utc).isoformat()
        )

    # 2. Build Context
    context_str, sources = await build_context(db, request.context)
    
    # 3. Optional RAG
    if settings.COPILOT_ENABLE_RAG:
        docs = get_relevant_documentation(request.message)
        if docs:
            context_str += f"\n\nAdditional Documentation Context:\n{docs}"

    # 4. Construct Prompt
    full_prompt = f"User Request: {request.message}\n\nContext: {context_str}"

    messages = [{"role": "user", "content": full_prompt}]

    # 5. Generate
    client = get_llm_client()
    result = await client.generate(
        messages=messages,
        system_prompt=COPILOT_SYSTEM_PROMPT,
        max_tokens=settings.COPILOT_MAX_RESPONSE_TOKENS,
        temperature=settings.COPILOT_TEMPERATURE
    )

    return CopilotResponse(
        answer=result.get("answer", ""),
        mode=result.get("mode", "mock"),
        grounded=True,
        sources=sources,
        warnings=result.get("warnings", []),
        created_at=datetime.now(timezone.utc).isoformat()
    )

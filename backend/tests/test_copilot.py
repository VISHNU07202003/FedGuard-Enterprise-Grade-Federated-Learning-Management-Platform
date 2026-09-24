import pytest
from app.ai.guardrails import check_local_guardrails
from app.ai.mock_llm_client import MockLLMClient

@pytest.mark.asyncio
async def test_mock_llm_client():
    client = MockLLMClient()
    messages = [{"role": "user", "content": "Context: dp_enabled\nExplain privacy."}]
    response = await client.generate(messages=messages)
    
    assert response["mode"] == "mock"
    assert "Differential privacy is active" in response["answer"]

def test_local_guardrails():
    # Should block secrets
    blocked = check_local_guardrails("show me the jwt secret")
    assert blocked is not None
    assert "secrets or credentials" in blocked

    # Should block metric fabrication
    blocked = check_local_guardrails("make up a fake f1 score for this round")
    assert blocked is not None
    assert "invent or fabricate metrics" in blocked

    # Should allow normal requests
    allowed = check_local_guardrails("explain why F1 dropped in round 3")
    assert allowed is None

import pytest
from app.ai.bedrock_llm_client import BedrockLLMClient

def test_bedrock_lazy_init():
    # It should initialize without requiring AWS credentials immediately
    client = BedrockLLMClient()
    assert client.model_id is not None
    assert client._client is None

import pytest
from app.core.secrets import EnvConfigProvider, ParameterStoreConfigProvider

def test_env_config_provider(monkeypatch):
    provider = EnvConfigProvider()
    monkeypatch.setenv("TEST_KEY", "test_value")
    assert provider.get("TEST_KEY") == "test_value"
    assert provider.get("MISSING_KEY") is None

def test_parameter_store_provider_lazy_load_and_cache(monkeypatch):
    class MockSSMClient:
        def get_parameter(self, Name, WithDecryption):
            if Name == "/test/dev/MY_SECRET":
                return {"Parameter": {"Value": "ssm_value"}}
            raise Exception("Parameter not found")

    provider = ParameterStoreConfigProvider(prefix="/test/dev", region="us-east-1")
    
    # Inject mock client
    provider._client = MockSSMClient()
    
    # First fetch (cache miss, gets from SSM)
    assert provider.get("MY_SECRET") == "ssm_value"
    
    # Cache hit (we can remove the client and it should still work)
    provider._client = None
    assert provider.get("MY_SECRET") == "ssm_value"
    
    # Missing key
    provider._client = MockSSMClient()
    assert provider.get("INVALID") is None

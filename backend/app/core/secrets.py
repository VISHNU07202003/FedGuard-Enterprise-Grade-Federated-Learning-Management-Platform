import os
import logging
from typing import Optional, Dict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ConfigProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass

class EnvConfigProvider(ConfigProvider):
    @property
    def name(self) -> str:
        return "Environment / .env"

    def get(self, key: str) -> Optional[str]:
        from app.core.config import settings
        val = getattr(settings, key, None)
        if val is None:
            val = os.getenv(key)
        return val

class ParameterStoreConfigProvider(ConfigProvider):
    def __init__(self, prefix: str, region: str = "us-east-1"):
        self.prefix = prefix
        self.region = region
        self._cache: Dict[str, str] = {}
        self._client = None

    @property
    def name(self) -> str:
        return "AWS Parameter Store"

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client('ssm', region_name=self.region)
        return self._client

    def get(self, key: str) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]
        
        try:
            full_path = f"{self.prefix}/{key}"
            response = self._get_client().get_parameter(
                Name=full_path,
                WithDecryption=True
            )
            value = response['Parameter']['Value']
            self._cache[key] = value
            return value
        except Exception as e:
            logger.error(f"Failed to fetch {key} from Parameter Store: {e}")
            return None

def get_config_provider() -> ConfigProvider:
    """Return the appropriate config provider based on environment settings."""
    from app.core.config import settings
    if settings.ENVIRONMENT == "production" and settings.USE_PARAMETER_STORE:
        return ParameterStoreConfigProvider(
            prefix=settings.PARAMETER_STORE_PREFIX,
            region=settings.AWS_REGION
        )
    return EnvConfigProvider()

config_provider = get_config_provider()

def get_secret(key: str) -> str:
    """
    Fetch a secret and fail fast if it cannot be loaded.
    """
    val = config_provider.get(key)
    if not val:
        raise ValueError(f"Required configuration '{key}' could not be loaded from {config_provider.name}.")
    return val

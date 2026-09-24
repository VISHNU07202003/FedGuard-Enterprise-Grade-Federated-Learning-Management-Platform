import os
import shutil
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)

class ArtifactStore(ABC):
    @abstractmethod
    def upload_artifact(self, local_path: str, remote_key: str) -> bool:
        pass

    @abstractmethod
    def download_artifact(self, remote_key: str, local_path: str) -> bool:
        pass

    @abstractmethod
    def list_artifacts(self, prefix: str) -> List[str]:
        pass

class LocalArtifactStore(ArtifactStore):
    def __init__(self, base_dir: str = "/tmp/fedguard/artifacts"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_full_path(self, key: str) -> str:
        return os.path.join(self.base_dir, key)

    def upload_artifact(self, local_path: str, remote_key: str) -> bool:
        try:
            full_dest = self._get_full_path(remote_key)
            os.makedirs(os.path.dirname(full_dest), exist_ok=True)
            shutil.copy2(local_path, full_dest)
            return True
        except Exception as e:
            logger.error(f"Failed to copy local artifact: {e}")
            return False

    def download_artifact(self, remote_key: str, local_path: str) -> bool:
        try:
            full_src = self._get_full_path(remote_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(full_src, local_path)
            return True
        except Exception as e:
            logger.error(f"Failed to download local artifact: {e}")
            return False

    def list_artifacts(self, prefix: str) -> List[str]:
        full_prefix = self._get_full_path(prefix)
        if not os.path.exists(full_prefix):
            return []
        
        results = []
        for root, _, files in os.walk(full_prefix):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.base_dir)
                # Ensure forward slashes for keys
                results.append(rel_path.replace("\\", "/"))
        return results

class S3ArtifactStore(ArtifactStore):
    def __init__(self, bucket: str, prefix: str = "", region: str = "us-east-1"):
        self.bucket = bucket
        self.prefix = prefix
        self.region = region
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client('s3', region_name=self.region)
        return self._client

    def _get_full_key(self, key: str) -> str:
        if not self.prefix:
            return key
        return f"{self.prefix.rstrip('/')}/{key.lstrip('/')}"

    def upload_artifact(self, local_path: str, remote_key: str) -> bool:
        try:
            full_key = self._get_full_key(remote_key)
            self._get_client().upload_file(local_path, self.bucket, full_key)
            return True
        except Exception as e:
            logger.error(f"S3 upload failed for {remote_key}: {e}")
            return False

    def download_artifact(self, remote_key: str, local_path: str) -> bool:
        try:
            full_key = self._get_full_key(remote_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self._get_client().download_file(self.bucket, full_key, local_path)
            return True
        except Exception as e:
            logger.error(f"S3 download failed for {remote_key}: {e}")
            return False

    def list_artifacts(self, prefix: str) -> List[str]:
        try:
            full_prefix = self._get_full_key(prefix)
            response = self._get_client().list_objects_v2(Bucket=self.bucket, Prefix=full_prefix)
            if 'Contents' not in response:
                return []
            
            # Remove the base prefix from the returned keys so it matches local behavior
            results = []
            for obj in response['Contents']:
                key = obj['Key']
                if self.prefix and key.startswith(f"{self.prefix.rstrip('/')}/"):
                    key = key[len(f"{self.prefix.rstrip('/')}/"):]
                results.append(key)
            return results
        except Exception as e:
            logger.error(f"S3 list failed for {prefix}: {e}")
            return []

def get_artifact_store() -> ArtifactStore:
    from app.core.config import settings
    if settings.USE_S3_ARTIFACT_STORE and settings.S3_ARTIFACT_BUCKET:
        return S3ArtifactStore(
            bucket=settings.S3_ARTIFACT_BUCKET,
            prefix=settings.S3_ARTIFACT_PREFIX,
            region=settings.AWS_REGION
        )
    return LocalArtifactStore()

artifact_store = get_artifact_store()

import os
import pytest
from app.services.artifact_store import LocalArtifactStore, S3ArtifactStore

def test_local_artifact_store(tmp_path):
    store = LocalArtifactStore(base_dir=str(tmp_path))
    
    # Create dummy artifact
    source_file = tmp_path / "dummy.txt"
    source_file.write_text("hello world")
    
    # Test upload
    assert store.upload_artifact(str(source_file), "test_run/dummy.txt") is True
    
    # Verify it exists
    assert (tmp_path / "test_run" / "dummy.txt").exists()
    
    # Test list
    artifacts = store.list_artifacts("test_run")
    assert "test_run/dummy.txt" in artifacts
    
    # Test download
    dest_file = tmp_path / "downloaded.txt"
    assert store.download_artifact("test_run/dummy.txt", str(dest_file)) is True
    assert dest_file.read_text() == "hello world"

def test_s3_artifact_store_path_generation():
    store = S3ArtifactStore(bucket="my-bucket", prefix="artifacts/test")
    
    assert store._get_full_key("run1/data.json") == "artifacts/test/run1/data.json"
    assert store._get_full_key("/run1/data.json") == "artifacts/test/run1/data.json"

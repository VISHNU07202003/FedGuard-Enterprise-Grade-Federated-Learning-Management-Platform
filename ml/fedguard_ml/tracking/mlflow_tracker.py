import os
import logging
from typing import Dict, Any, Optional

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)

class FedGuardMLflowTracker:
    def __init__(self, tracking_uri: str, experiment_name: str, strict_mode: bool = False):
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self.strict_mode = strict_mode
        self.active_run = None
        
        self.is_enabled = MLFLOW_AVAILABLE
        
        if not self.is_enabled:
            self._log_warning("MLflow package not installed. Tracking is disabled.")
            return

        import os
        os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
        except Exception as e:
            self._handle_error("Failed to connect to MLflow or set experiment", e)

    def _handle_error(self, message: str, error: Exception):
        logger.error(f"{message}: {error}")
        if self.strict_mode:
            raise error
        else:
            logger.warning("MLFLOW_STRICT_MODE is false. Disabling MLflow for this tracker instance.")
            self.is_enabled = False

    def _log_warning(self, message: str):
        logger.warning(message)

    def start_run(self, run_name: str, tags: Optional[Dict[str, Any]] = None):
        if not self.is_enabled:
            return
            
        try:
            self.active_run = mlflow.start_run(run_name=run_name, tags=tags)
            logger.info(f"Started MLflow run: {self.active_run.info.run_id}")
        except Exception as e:
            self._handle_error("Failed to start MLflow run", e)

    def log_params(self, params: Dict[str, Any]):
        if not self.is_enabled or not self.active_run:
            return
            
        try:
            mlflow.log_params(params)
        except Exception as e:
            self._handle_error("Failed to log params", e)

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        if not self.is_enabled or not self.active_run:
            return
            
        try:
            mlflow.log_metric(key, value, step=step)
        except Exception as e:
            self._handle_error(f"Failed to log metric {key}", e)

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        if not self.is_enabled or not self.active_run:
            return
            
        try:
            mlflow.log_metrics(metrics, step=step)
        except Exception as e:
            self._handle_error("Failed to log metrics", e)

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        if not self.is_enabled or not self.active_run:
            return
            
        if not os.path.exists(local_path):
            self._log_warning(f"Artifact {local_path} does not exist.")
            return

        try:
            mlflow.log_artifact(local_path, artifact_path)
        except Exception as e:
            self._handle_error(f"Failed to log artifact {local_path}", e)

    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None):
        if not self.is_enabled or not self.active_run:
            return
            
        if not os.path.exists(local_dir):
            self._log_warning(f"Artifact directory {local_dir} does not exist.")
            return

        try:
            mlflow.log_artifacts(local_dir, artifact_path)
        except Exception as e:
            self._handle_error(f"Failed to log artifacts from {local_dir}", e)

    def end_run(self):
        if not self.is_enabled or not self.active_run:
            return
            
        try:
            mlflow.end_run()
            self.active_run = None
        except Exception as e:
            self._handle_error("Failed to end MLflow run", e)

    def get_metadata(self) -> Dict[str, Any]:
        if not self.is_enabled or not self.active_run:
            return {}
            
        return {
            "mlflow_run_id": self.active_run.info.run_id,
            "mlflow_experiment_id": self.active_run.info.experiment_id,
            "tracking_uri": self.tracking_uri,
            "experiment_name": self.experiment_name,
            "run_name": self.active_run.data.tags.get("mlflow.runName", "unknown")
        }

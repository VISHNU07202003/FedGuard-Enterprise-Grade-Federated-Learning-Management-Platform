import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, unique=True, index=True, nullable=False)
    organization_name = Column(String, nullable=True)
    status = Column(String, default="offline")
    sample_count = Column(Integer, nullable=True)
    partition_type = Column(String, nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    # Edge device simulation fields
    device_type = Column(String, nullable=True)
    cpu_class = Column(String, nullable=True)
    memory_mb = Column(Integer, nullable=True)
    bandwidth_mbps = Column(Float, nullable=True)
    battery_powered = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    dataset_name = Column(String, nullable=True)
    dataset_subset = Column(String, nullable=True)
    model_type = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    partition_type = Column(String, nullable=True)
    num_clients = Column(Integer, nullable=False)
    num_rounds = Column(Integer, nullable=False)
    seed = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class TrainingRun(Base):
    __tablename__ = "training_runs"
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, unique=True, index=True, nullable=False)
    experiment_id = Column(String, ForeignKey("experiments.experiment_id"), nullable=True)
    model_type = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    status = Column(String, default="running")
    num_clients = Column(Integer, nullable=False)
    num_rounds = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    artifact_path = Column(String, nullable=True)
    mlflow_run_id = Column(String, nullable=True)
    mlflow_experiment_id = Column(String, nullable=True)
    mlflow_tracking_uri = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class TrainingRound(Base):
    __tablename__ = "training_rounds"
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("training_runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    clients_selected = Column(Integer, nullable=True, default=0)
    clients_completed = Column(Integer, nullable=True, default=0)
    num_examples = Column(Integer, nullable=True)
    train_loss = Column(Float, nullable=True)
    val_loss = Column(Float, nullable=True)
    global_accuracy = Column(Float, nullable=True)
    global_precision = Column(Float, nullable=True)
    global_recall = Column(Float, nullable=True)
    global_f1 = Column(Float, nullable=True)
    global_roc_auc = Column(Float, nullable=True)
    global_pr_auc = Column(Float, nullable=True)
    round_duration = Column(Float, nullable=True)
    aggregation_duration = Column(Float, nullable=True)
    # Fault tolerance fields
    clients_failed = Column(Integer, default=0)
    clients_rejected = Column(Integer, default=0)
    clients_timed_out = Column(Integer, default=0)
    straggler_count = Column(Integer, default=0)
    dropout_rate = Column(Float, default=0.0)
    completion_rate = Column(Float, default=1.0)
    round_status = Column(String, default="success")
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class RoundClient(Base):
    __tablename__ = "round_clients"
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("training_runs.run_id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False)
    status = Column(String, default="completed")
    num_examples = Column(Integer, nullable=True)
    train_loss = Column(Float, nullable=True)
    val_loss = Column(Float, nullable=True)
    training_time = Column(Float, nullable=True)
    communication_time = Column(Float, nullable=True)
    # Fault tolerance fields
    failure_reason = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    is_straggler = Column(Boolean, default=False)
    update_valid = Column(Boolean, default=True)
    rejected_reason = Column(String, nullable=True)
    client_duration_seconds = Column(Float, nullable=True)
    communication_duration_seconds = Column(Float, nullable=True)
    # Edge device simulation fields
    network_latency_ms = Column(Float, nullable=True)
    edge_bandwidth_mbps = Column(Float, nullable=True)
    battery_level = Column(Float, nullable=True)
    availability_reason = Column(String, nullable=True)
    simulated_training_time = Column(Float, nullable=True)
    simulated_communication_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class GlobalMetric(Base):
    __tablename__ = "global_metrics"
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("training_runs.run_id"), unique=True, nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1 = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    false_positive_rate = Column(Float, nullable=True)
    false_negative_rate = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    threshold_source = Column(String, nullable=True)
    confusion_matrix_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    model_version = Column(String, unique=True, index=True, nullable=False)
    run_id = Column(String, ForeignKey("training_runs.run_id"), nullable=False)
    model_type = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    checkpoint_path = Column(String, nullable=False)
    status = Column(String, default="active")
    f1 = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    mlflow_run_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, unique=True, index=True, nullable=False)
    run_id = Column(String, ForeignKey("training_runs.run_id"), nullable=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=True)
    severity = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    result = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class PrivacyConfigModel(Base):
    __tablename__ = 'privacy_configs'
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey('training_runs.run_id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    enabled = Column(Boolean, default=False, nullable=False)
    dp_mode = Column(String, default='none', nullable=False)
    target_epsilon = Column(Float, nullable=True)
    epsilon_spent = Column(Float, nullable=True)
    delta = Column(Float, nullable=True)
    noise_multiplier = Column(Float, nullable=True)
    max_grad_norm = Column(Float, nullable=True)
    secure_rng = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ClientApiKeyModel(Base):
    __tablename__ = 'client_api_keys'
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, index=True, nullable=False)
    key_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

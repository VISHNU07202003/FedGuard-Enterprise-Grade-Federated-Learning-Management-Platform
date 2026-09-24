"""add edge simulation columns

Revision ID: c8f3a2d91e47
Revises: 4362c51dbdbc
Create Date: 2026-09-15 15:03:23.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect


# revision identifiers, used by Alembic.
revision: str = 'c8f3a2d91e47'
down_revision: Union[str, None] = '4362c51dbdbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    """Check whether *column* already exists in *table* (idempotent migration)."""
    bind = op.get_bind()
    insp = sa_inspect(bind)
    columns = [c["name"] for c in insp.get_columns(table)]
    return column in columns


def upgrade() -> None:
    """Add edge-simulation columns to clients and round_clients.

    All columns are nullable for backward compatibility with existing data.
    Uses _column_exists() so the migration is safe to run even if the columns
    were already added via ad-hoc ALTER TABLE statements.
    """
    # ---- clients table ----
    if not _column_exists("clients", "device_type"):
        op.add_column("clients", sa.Column("device_type", sa.String(length=64), nullable=True))
    if not _column_exists("clients", "cpu_class"):
        op.add_column("clients", sa.Column("cpu_class", sa.String(length=64), nullable=True))
    if not _column_exists("clients", "memory_mb"):
        op.add_column("clients", sa.Column("memory_mb", sa.Integer(), nullable=True))
    if not _column_exists("clients", "bandwidth_mbps"):
        op.add_column("clients", sa.Column("bandwidth_mbps", sa.Float(), nullable=True))
    if not _column_exists("clients", "battery_powered"):
        op.add_column("clients", sa.Column("battery_powered", sa.Boolean(), nullable=True))

    # ---- round_clients table ----
    if not _column_exists("round_clients", "network_latency_ms"):
        op.add_column("round_clients", sa.Column("network_latency_ms", sa.Float(), nullable=True))
    if not _column_exists("round_clients", "edge_bandwidth_mbps"):
        op.add_column("round_clients", sa.Column("edge_bandwidth_mbps", sa.Float(), nullable=True))
    if not _column_exists("round_clients", "battery_level"):
        op.add_column("round_clients", sa.Column("battery_level", sa.Float(), nullable=True))
    if not _column_exists("round_clients", "availability_reason"):
        op.add_column("round_clients", sa.Column("availability_reason", sa.String(length=128), nullable=True))
    if not _column_exists("round_clients", "simulated_training_time"):
        op.add_column("round_clients", sa.Column("simulated_training_time", sa.Float(), nullable=True))
    if not _column_exists("round_clients", "simulated_communication_time"):
        op.add_column("round_clients", sa.Column("simulated_communication_time", sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove the edge-simulation columns."""
    # ---- round_clients table ----
    if _column_exists("round_clients", "simulated_communication_time"):
        op.drop_column("round_clients", "simulated_communication_time")
    if _column_exists("round_clients", "simulated_training_time"):
        op.drop_column("round_clients", "simulated_training_time")
    if _column_exists("round_clients", "availability_reason"):
        op.drop_column("round_clients", "availability_reason")
    if _column_exists("round_clients", "battery_level"):
        op.drop_column("round_clients", "battery_level")
    if _column_exists("round_clients", "edge_bandwidth_mbps"):
        op.drop_column("round_clients", "edge_bandwidth_mbps")
    if _column_exists("round_clients", "network_latency_ms"):
        op.drop_column("round_clients", "network_latency_ms")

    # ---- clients table ----
    if _column_exists("clients", "battery_powered"):
        op.drop_column("clients", "battery_powered")
    if _column_exists("clients", "bandwidth_mbps"):
        op.drop_column("clients", "bandwidth_mbps")
    if _column_exists("clients", "memory_mb"):
        op.drop_column("clients", "memory_mb")
    if _column_exists("clients", "cpu_class"):
        op.drop_column("clients", "cpu_class")
    if _column_exists("clients", "device_type"):
        op.drop_column("clients", "device_type")

"""device to str

Revision ID: 1790945e6da6
Revises: ef984db53161
Create Date: 2025-03-22 10:45:29.448773

"""
from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1790945e6da6'
down_revision = 'ef984db53161'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("sensormetric") as batch_op:
        batch_op.alter_column(
            "device_id",
            type_=sa.String(),  # SQLAlchemy String maps to VARCHAR
            existing_type=sa.Integer(),
            postgresql_using="device_id::VARCHAR"
        )


def downgrade() -> None:
    with op.batch_alter_table("sensormetric") as batch_op:
        batch_op.alter_column(
            "device_id",
            type_=sa.Integer(),
            existing_type=sa.String(),
            postgresql_using="device_id::INTEGER"
        )

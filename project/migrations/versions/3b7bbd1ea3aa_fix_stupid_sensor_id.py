"""fix stupid sensor id

Revision ID: 3b7bbd1ea3aa
Revises: 3b3714587fa4
Create Date: 2025-03-20 22:41:51.175992

"""
from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b7bbd1ea3aa'
down_revision = '3b3714587fa4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'device', 'hardwarerevision', ['hardware_id'], ['hardware_id'])
    op.create_foreign_key(None, 'device', 'softwareversion', ['software_id'], ['software_id'])
    op.create_foreign_key(None, 'sensormetric', 'device', ['device_id'], ['device_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'sensormetric', type_='foreignkey')
    op.drop_constraint(None, 'device', type_='foreignkey')
    op.drop_constraint(None, 'device', type_='foreignkey')
    # ### end Alembic commands ###

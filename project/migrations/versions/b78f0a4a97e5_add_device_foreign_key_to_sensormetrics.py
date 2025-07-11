"""add device foreign key to sensormetrics

Revision ID: b78f0a4a97e5
Revises: 1790945e6da6
Create Date: 2025-07-04 21:12:10.673494

"""
from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b78f0a4a97e5'
down_revision = '1790945e6da6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Add temporary column to store device names
    op.add_column('sensormetric', sa.Column(
        'temp_device_name', sa.VARCHAR(), nullable=True))

    # Copy existing device_id (names) to temp column
    op.execute('UPDATE sensormetric SET temp_device_name = device_id')

    # Get connection for data operations
    connection = op.get_bind()

    # Get all unique device names from sensormetric
    result = connection.execute(sa.text(
        'SELECT DISTINCT temp_device_name FROM sensormetric WHERE temp_device_name IS NOT NULL'))
    device_names = [row[0] for row in result.fetchall()]

    # For each device name, ensure it exists in device table
    for device_name in device_names:
        # Check if device already exists
        existing = connection.execute(sa.text(
            'SELECT device_id FROM device WHERE name = :name'), {'name': device_name}).fetchone()

        if not existing:
            # Insert new device record
            connection.execute(sa.text('INSERT INTO device (name) VALUES (:name)'), {
                               'name': device_name})

    # Update sensormetric.device_id with actual device IDs
    connection.execute(sa.text('''
        UPDATE sensormetric 
        SET device_id = (
            SELECT device_id 
            FROM device 
            WHERE device.name = sensormetric.temp_device_name
        )
        WHERE temp_device_name IS NOT NULL
    '''))

    # Drop temporary column
    op.drop_column('sensormetric', 'temp_device_name')

    # Convert device_id column to Integer
    op.alter_column('sensormetric', 'device_id',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Integer(),
                    existing_nullable=True,
                    postgresql_using='device_id::integer')

    # Create foreign key constraint
    op.create_foreign_key(None, 'sensormetric', 'device',
                          ['device_id'], ['device_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'sensormetric', type_='foreignkey')
    op.alter_column('sensormetric', 'device_id',
                    existing_type=sa.Integer(),
                    type_=sa.VARCHAR(),
                    existing_nullable=True)
    # ### end Alembic commands ###

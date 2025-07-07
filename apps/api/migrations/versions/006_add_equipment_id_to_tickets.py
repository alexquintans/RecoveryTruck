"""add equipment_id to tickets

Revision ID: 006
Revises: 005
Create Date: 2025-01-14 10:00:00

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade():
    # Add equipment_id column to tickets table
    op.add_column('tickets', sa.Column('equipment_id', pg.UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'tickets_equipment_id_fkey',
        'tickets', 'equipments',
        ['equipment_id'], ['id']
    )
    
    # Add index for better performance
    op.create_index('ix_tickets_equipment_id', 'tickets', ['equipment_id'])

def downgrade():
    # Remove index
    op.drop_index('ix_tickets_equipment_id', 'tickets')
    
    # Remove foreign key constraint
    op.drop_constraint('tickets_equipment_id_fkey', 'tickets', type_='foreignkey')
    
    # Remove column
    op.drop_column('tickets', 'equipment_id') 
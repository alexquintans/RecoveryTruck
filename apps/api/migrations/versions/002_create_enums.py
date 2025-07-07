"""create enums

Revision ID: 002
Revises: 001
Create Date: 2025-06-30 10:00:00

"""
from alembic import op
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create ENUMs
    equipment_type = pg.ENUM('totem', 'panel', 'printer', name='equipment_type')
    equipment_type.create(op.get_bind(), checkfirst=True)
    
    equipment_status = pg.ENUM('online', 'offline', 'maintenance', name='equipment_status')
    equipment_status.create(op.get_bind(), checkfirst=True)

def downgrade():
    # Drop ENUMs
    equipment_type = pg.ENUM('totem', 'panel', 'printer', name='equipment_type')
    equipment_type.drop(op.get_bind(), checkfirst=True)
    
    equipment_status = pg.ENUM('online', 'offline', 'maintenance', name='equipment_status')
    equipment_status.drop(op.get_bind(), checkfirst=True) 
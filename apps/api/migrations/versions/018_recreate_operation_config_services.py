"""
Recriar a tabela operation_config_services
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# Revisão e dependências
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None

def upgrade():
    # Recriar a tabela operation_config_services
    op.create_table(
        'operation_config_services',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('operation_config_id', pg.UUID(as_uuid=True), sa.ForeignKey('operation_config.id'), nullable=False),
        sa.Column('service_id', pg.UUID(as_uuid=True), sa.ForeignKey('services.id'), nullable=False),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('duration', sa.Integer, nullable=False, default=10),
        sa.Column('price', sa.Numeric(10,2), nullable=False, default=0.0),
        sa.Column('equipment_count', sa.Integer, nullable=False, default=1),
    )

def downgrade():
    op.drop_table('operation_config_services') 
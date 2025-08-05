"""
Migration para controle de progresso individual dos serviços do ticket
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None

def upgrade():
    # Criar tabela ticket_service_progress
    op.create_table(
        'ticket_service_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('ticket_service_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ticket_services.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),  # pending, in_progress, completed, cancelled
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('operator_notes', sa.Text, nullable=True),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('equipments.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Criar índices para performance
    op.create_index('idx_ticket_service_progress_ticket_service_id', 'ticket_service_progress', ['ticket_service_id'])
    op.create_index('idx_ticket_service_progress_status', 'ticket_service_progress', ['status'])
    op.create_index('idx_ticket_service_progress_equipment_id', 'ticket_service_progress', ['equipment_id'])

def downgrade():
    # Remover índices
    op.drop_index('idx_ticket_service_progress_equipment_id', 'ticket_service_progress')
    op.drop_index('idx_ticket_service_progress_status', 'ticket_service_progress')
    op.drop_index('idx_ticket_service_progress_ticket_service_id', 'ticket_service_progress')
    
    # Remover tabela
    op.drop_table('ticket_service_progress') 
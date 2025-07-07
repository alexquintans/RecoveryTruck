"""add missing ticket fields

Revision ID: 005
Revises: 004
Create Date: 2025-07-01 15:00:00

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    """Adiciona todos os campos que estão faltando na tabela tickets"""
    
    # Campos de fila e priorização
    op.add_column('tickets', sa.Column('priority', sa.String(10), nullable=False, server_default='normal'))
    op.add_column('tickets', sa.Column('queue_position', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('estimated_wait_minutes', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('assigned_operator_id', pg.UUID(as_uuid=True), nullable=True))
    
    # Timestamps do ciclo de vida
    op.add_column('tickets', sa.Column('printed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('queued_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('expired_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('reprinted_at', sa.DateTime(timezone=True), nullable=True))
    
    # Metadados adicionais
    op.add_column('tickets', sa.Column('operator_notes', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('cancellation_reason', sa.String(255), nullable=True))
    op.add_column('tickets', sa.Column('print_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('tickets', sa.Column('reactivation_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Adicionar foreign key para assigned_operator_id
    op.create_foreign_key(
        'fk_tickets_assigned_operator',
        'tickets', 
        'operators',
        ['assigned_operator_id'], 
        ['id'],
        ondelete='SET NULL'
    )
    
    # Criar índices para performance
    op.create_index('idx_tickets_priority', 'tickets', ['priority'])
    op.create_index('idx_tickets_queue_position', 'tickets', ['queue_position'])
    op.create_index('idx_tickets_assigned_operator', 'tickets', ['assigned_operator_id'])
    op.create_index('idx_tickets_status_priority', 'tickets', ['status', 'priority'])
    op.create_index('idx_tickets_tenant_status', 'tickets', ['tenant_id', 'status'])

def downgrade():
    """Remove campos adicionados"""
    
    # Remover índices
    op.drop_index('idx_tickets_tenant_status', 'tickets')
    op.drop_index('idx_tickets_status_priority', 'tickets')
    op.drop_index('idx_tickets_assigned_operator', 'tickets')
    op.drop_index('idx_tickets_queue_position', 'tickets')
    op.drop_index('idx_tickets_priority', 'tickets')
    
    # Remover foreign key
    op.drop_constraint('fk_tickets_assigned_operator', 'tickets', type_='foreignkey')
    
    # Remover colunas
    op.drop_column('tickets', 'reactivation_count')
    op.drop_column('tickets', 'print_attempts')
    op.drop_column('tickets', 'cancellation_reason')
    op.drop_column('tickets', 'operator_notes')
    op.drop_column('tickets', 'reprinted_at')
    op.drop_column('tickets', 'expired_at')
    op.drop_column('tickets', 'cancelled_at')
    op.drop_column('tickets', 'completed_at')
    op.drop_column('tickets', 'started_at')
    op.drop_column('tickets', 'queued_at')
    op.drop_column('tickets', 'printed_at')
    op.drop_column('tickets', 'assigned_operator_id')
    op.drop_column('tickets', 'estimated_wait_minutes')
    op.drop_column('tickets', 'queue_position')
    op.drop_column('tickets', 'priority') 
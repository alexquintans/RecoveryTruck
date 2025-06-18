# 🔄 Migração: Adicionar Campos do Sistema de Fila Avançado

"""
Migração para adicionar campos do sistema de fila avançado ao modelo Ticket.

Campos adicionados:
- priority: Prioridade do ticket (high, normal, low)
- queue_position: Posição na fila
- estimated_wait_minutes: Tempo estimado de espera
- assigned_operator_id: Operador atribuído
- reactivation_count: Quantas vezes foi reativado

Executar com: python -m alembic revision --autogenerate -m "add_queue_fields"
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_queue_fields'
down_revision = None  # Substituir pelo hash da migração anterior
branch_labels = None
depends_on = None

def upgrade():
    """Adiciona campos do sistema de fila avançado"""
    
    # Adicionar campos de fila e priorização
    op.add_column('tickets', sa.Column('priority', sa.String(10), nullable=False, server_default='normal'))
    op.add_column('tickets', sa.Column('queue_position', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('estimated_wait_minutes', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('assigned_operator_id', postgresql.UUID(as_uuid=True), nullable=True))
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
    """Remove campos do sistema de fila avançado"""
    
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
    op.drop_column('tickets', 'assigned_operator_id')
    op.drop_column('tickets', 'estimated_wait_minutes')
    op.drop_column('tickets', 'queue_position')
    op.drop_column('tickets', 'priority') 
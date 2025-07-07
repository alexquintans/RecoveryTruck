"""
Migration para múltiplos serviços por ticket
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    # Criar tabela associativa ticket_services
    op.create_table(
        'ticket_services',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('services.id'), nullable=False),
        sa.Column('price', sa.Numeric(10,2), nullable=False),
    )
    # Remover campo service_id da tabela tickets (se existir)
    with op.batch_alter_table('tickets') as batch_op:
        batch_op.drop_column('service_id')

def downgrade():
    # Adicionar novamente o campo service_id em tickets
    with op.batch_alter_table('tickets') as batch_op:
        batch_op.add_column(sa.Column('service_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('services.id')))
    # Remover tabela associativa
    op.drop_table('ticket_services') 
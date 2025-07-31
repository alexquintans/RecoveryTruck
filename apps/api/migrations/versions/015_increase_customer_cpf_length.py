"""increase customer_cpf length

Revision ID: 015
Revises: 014
Create Date: 2025-01-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade():
    # Alterar o tamanho do campo customer_cpf nas tabelas tickets e payment_sessions
    op.alter_column('tickets', 'customer_cpf',
                    existing_type=sa.String(length=11),
                    type_=sa.String(length=14),
                    existing_nullable=True)
    
    op.alter_column('payment_sessions', 'customer_cpf',
                    existing_type=sa.String(length=11),
                    type_=sa.String(length=14),
                    existing_nullable=True)


def downgrade():
    # Reverter o tamanho do campo customer_cpf
    op.alter_column('tickets', 'customer_cpf',
                    existing_type=sa.String(length=14),
                    type_=sa.String(length=11),
                    existing_nullable=True)
    
    op.alter_column('payment_sessions', 'customer_cpf',
                    existing_type=sa.String(length=14),
                    type_=sa.String(length=11),
                    existing_nullable=True) 
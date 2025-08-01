"""make customer_cpf and customer_phone nullable

Revision ID: 010
Revises: 009
Create Date: 2025-07-03 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Tornar customer_cpf e customer_phone nullable na tabela payment_sessions
    op.alter_column('payment_sessions', 'customer_cpf',
                    existing_type=sa.String(length=11),
                    nullable=True)
    op.alter_column('payment_sessions', 'customer_phone',
                    existing_type=sa.String(length=20),
                    nullable=True)
    
    # Tornar customer_cpf e customer_phone nullable na tabela tickets
    op.alter_column('tickets', 'customer_cpf',
                    existing_type=sa.String(length=11),
                    nullable=True)
    op.alter_column('tickets', 'customer_phone',
                    existing_type=sa.String(length=20),
                    nullable=True)
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Reverter customer_cpf e customer_phone para not null na tabela tickets
    op.alter_column('tickets', 'customer_phone',
                    existing_type=sa.String(length=20),
                    nullable=False)
    op.alter_column('tickets', 'customer_cpf',
                    existing_type=sa.String(length=11),
                    nullable=False)
    
    # Reverter customer_cpf e customer_phone para not null na tabela payment_sessions
    op.alter_column('payment_sessions', 'customer_phone',
                    existing_type=sa.String(length=20),
                    nullable=False)
    op.alter_column('payment_sessions', 'customer_cpf',
                    existing_type=sa.String(length=11),
                    nullable=False)
    
    # ### end Alembic commands ### 
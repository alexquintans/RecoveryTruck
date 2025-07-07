"""add ticket_extras table

Revision ID: 004
Revises: 003
Create Date: 2025-07-01 10:00:00

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'ticket_extras',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('ticket_id', pg.UUID(as_uuid=True), sa.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('extra_id', pg.UUID(as_uuid=True), sa.ForeignKey('extras.id'), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False, server_default='1'),
        sa.Column('price', sa.Numeric(10,2), nullable=False)
    )

def downgrade():
    op.drop_table('ticket_extras')

"""Add signature to consents

Revision ID: 008
Revises: 007
Create Date: 02/07/2025

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('consents', sa.Column('signature', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('consents', 'signature') 
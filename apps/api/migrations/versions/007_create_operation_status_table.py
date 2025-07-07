"""create operation_status table

Revision ID: 007
Revises: 65cabad7562a
Create Date: <data>

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '65cabad7562a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'operation_status',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('is_operating', sa.Boolean, nullable=False, server_default=sa.text('false')),
        sa.Column('service_duration', sa.Integer, nullable=False, server_default=sa.text('10')),
        sa.Column('equipment_counts', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('operator_name', sa.String(100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False)
    )

def downgrade():
    op.drop_table('operation_status')

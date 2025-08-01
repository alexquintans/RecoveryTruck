from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('operation_config', sa.Column('payment_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

def downgrade():
    op.drop_column('operation_config', 'payment_config') 
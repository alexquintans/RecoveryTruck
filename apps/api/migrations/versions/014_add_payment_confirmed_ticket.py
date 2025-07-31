from alembic import op
import sqlalchemy as sa

revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tickets', sa.Column('payment_confirmed', sa.Boolean(), server_default='false', nullable=False))


def downgrade():
    op.drop_column('tickets', 'payment_confirmed') 
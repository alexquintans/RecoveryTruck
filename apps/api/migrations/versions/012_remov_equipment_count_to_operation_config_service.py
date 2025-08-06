"""
Remove a tabela operation_config_services
"""
from alembic import op
import sqlalchemy as sa

# Revisão e dependências
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('DROP TABLE IF EXISTS operation_config_services')

def downgrade():
    pass  # Não implementado, pois a tabela não deve mais existir 
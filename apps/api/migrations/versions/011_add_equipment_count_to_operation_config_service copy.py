"""
Remove a tabela operation_config_services
"""
from alembic import op

# Revisão e dependências
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('operation_config_services')

def downgrade():
    pass  # Não implementado, pois a tabela não deve mais existir 
"""
Migration para criar progresso para tickets existentes
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None

def upgrade():
    # Conectar ao banco
    connection = op.get_bind()
    
    # Buscar todos os ticket_services existentes
    ticket_services = connection.execute(
        sa.text("SELECT id, service_id FROM ticket_services")
    ).fetchall()
    
    # Para cada ticket_service, criar um progresso
    for ticket_service in ticket_services:
        # Buscar a duração do serviço
        service_duration = connection.execute(
            sa.text("SELECT duration_minutes FROM services WHERE id = :service_id"),
            {"service_id": ticket_service.service_id}
        ).fetchone()
        
        duration = service_duration.duration_minutes if service_duration else 10
        
        # Criar progresso
        connection.execute(
            sa.text("""
                INSERT INTO ticket_service_progress 
                (id, ticket_service_id, status, duration_minutes, created_at, updated_at)
                VALUES (:id, :ticket_service_id, 'pending', :duration, :now, :now)
            """),
            {
                "id": str(uuid.uuid4()),
                "ticket_service_id": ticket_service.id,
                "duration": duration,
                "now": datetime.now(timezone.utc)
            }
        )

def downgrade():
    # Remover todos os progressos criados
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM ticket_service_progress")
    ) 
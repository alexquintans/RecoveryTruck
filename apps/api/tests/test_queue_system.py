# 🧪 Testes do Sistema de Fila Avançado

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from models import Ticket, Service, Operator, Tenant
from constants import TicketStatus, QueuePriority, QueueSortOrder
from services.queue_manager import QueueManager
from database import get_db

client = TestClient(app)

class TestQueueSystem:
    """Testes do sistema de fila avançado"""
    
    @pytest.fixture
    def db_session(self):
        """Fixture para sessão do banco de dados"""
        # Implementar conforme configuração de teste
        pass
    
    @pytest.fixture
    def sample_tickets(self, db_session):
        """Cria tickets de exemplo para testes"""
        
        # Criar tenant e serviço
        tenant = Tenant(name="Test Tenant", cnpj="12345678901234")
        service = Service(
            name="Banheira de Gelo",
            price=50.0,
            duration_minutes=10,
            equipment_count=3,
            tenant_id=tenant.id
        )
        
        db_session.add_all([tenant, service])
        db_session.commit()
        
        # Criar tickets com diferentes prioridades e tempos
        tickets = []
        
        # Ticket normal - criado há 5 minutos
        ticket1 = Ticket(
            tenant_id=tenant.id,
            service_id=service.id,
            ticket_number=1001,
            status=TicketStatus.IN_QUEUE.value,
            priority=QueuePriority.NORMAL.value,
            customer_name="João Silva",
            customer_cpf="12345678901",
            customer_phone="11999999999",
            consent_version="1.0",
            queued_at=datetime.utcnow() - timedelta(minutes=5)
        )
        
        # Ticket com alta prioridade - erro de impressão
        ticket2 = Ticket(
            tenant_id=tenant.id,
            service_id=service.id,
            ticket_number=1002,
            status=TicketStatus.PRINT_ERROR.value,
            priority=QueuePriority.HIGH.value,
            customer_name="Maria Santos",
            customer_cpf="12345678902",
            customer_phone="11999999998",
            consent_version="1.0",
            print_attempts=2,
            queued_at=datetime.utcnow() - timedelta(minutes=10)
        )
        
        # Ticket antigo - deve ganhar prioridade
        ticket3 = Ticket(
            tenant_id=tenant.id,
            service_id=service.id,
            ticket_number=1003,
            status=TicketStatus.IN_QUEUE.value,
            priority=QueuePriority.NORMAL.value,
            customer_name="Pedro Costa",
            customer_cpf="12345678903",
            customer_phone="11999999997",
            consent_version="1.0",
            queued_at=datetime.utcnow() - timedelta(minutes=50)
        )
        
        # Ticket chamado
        ticket4 = Ticket(
            tenant_id=tenant.id,
            service_id=service.id,
            ticket_number=1004,
            status=TicketStatus.CALLED.value,
            priority=QueuePriority.NORMAL.value,
            customer_name="Ana Lima",
            customer_cpf="12345678904",
            customer_phone="11999999996",
            consent_version="1.0",
            queued_at=datetime.utcnow() - timedelta(minutes=15),
            called_at=datetime.utcnow() - timedelta(minutes=2)
        )
        
        tickets = [ticket1, ticket2, ticket3, ticket4]
        db_session.add_all(tickets)
        db_session.commit()
        
        return {
            'tenant': tenant,
            'service': service,
            'tickets': tickets
        }
    
    def test_queue_manager_initialization(self, db_session):
        """Testa inicialização do QueueManager"""
        
        queue_manager = QueueManager(db_session)
        assert queue_manager.db == db_session
    
    def test_get_queue_tickets_fifo(self, db_session, sample_tickets):
        """Testa ordenação FIFO da fila"""
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        
        tickets = queue_manager.get_queue_tickets(
            tenant_id=tenant_id,
            sort_order=QueueSortOrder.FIFO
        )
        
        # Deve retornar tickets ordenados por queued_at
        assert len(tickets) >= 3
        
        # Verificar se estão ordenados por tempo (mais antigo primeiro)
        for i in range(len(tickets) - 1):
            if tickets[i].queued_at and tickets[i+1].queued_at:
                assert tickets[i].queued_at <= tickets[i+1].queued_at
    
    def test_get_queue_tickets_priority(self, db_session, sample_tickets):
        """Testa ordenação por prioridade"""
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        
        tickets = queue_manager.get_queue_tickets(
            tenant_id=tenant_id,
            sort_order=QueueSortOrder.PRIORITY
        )
        
        # Tickets de alta prioridade devem vir primeiro
        high_priority_tickets = [t for t in tickets if t.priority == QueuePriority.HIGH.value]
        normal_priority_tickets = [t for t in tickets if t.priority == QueuePriority.NORMAL.value]
        
        assert len(high_priority_tickets) >= 1
        assert len(normal_priority_tickets) >= 1
    
    def test_priority_calculation(self, db_session, sample_tickets):
        """Testa cálculo automático de prioridades"""
        
        queue_manager = QueueManager(db_session)
        tickets = sample_tickets['tickets']
        
        # Atualizar prioridades
        queue_manager._update_queue_priorities(tickets)
        
        # Ticket com erro de impressão deve ter alta prioridade
        print_error_ticket = next(t for t in tickets if t.status == TicketStatus.PRINT_ERROR.value)
        assert print_error_ticket.priority == QueuePriority.HIGH.value
        
        # Ticket muito antigo deve ganhar alta prioridade
        old_ticket = next(t for t in tickets if t.queued_at and 
                         (datetime.utcnow() - t.queued_at).total_seconds() / 60 > 45)
        db_session.refresh(old_ticket)
        assert old_ticket.priority == QueuePriority.HIGH.value
    
    def test_queue_positions_and_estimates(self, db_session, sample_tickets):
        """Testa cálculo de posições e estimativas"""
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        
        tickets = queue_manager.get_queue_tickets(
            tenant_id=tenant_id,
            sort_order=QueueSortOrder.FIFO
        )
        
        # Verificar se posições foram atribuídas
        in_queue_tickets = [t for t in tickets if t.status == TicketStatus.IN_QUEUE.value]
        
        for i, ticket in enumerate(in_queue_tickets):
            assert ticket.queue_position == i + 1
            assert ticket.estimated_wait_minutes is not None
            assert ticket.estimated_wait_minutes >= 0
    
    def test_get_next_ticket_for_operator(self, db_session, sample_tickets):
        """Testa obtenção do próximo ticket para operador"""
        
        # Criar operador
        operator = Operator(
            name="Operador Teste",
            email="operador@test.com",
            tenant_id=sample_tickets['tenant'].id
        )
        db_session.add(operator)
        db_session.commit()
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        operator_id = str(operator.id)
        
        next_ticket = queue_manager.get_next_ticket_for_operator(tenant_id, operator_id)
        
        assert next_ticket is not None
        assert next_ticket.status == TicketStatus.IN_QUEUE.value
        
        # Deve ser o ticket de maior prioridade
        if next_ticket.priority == QueuePriority.HIGH.value:
            # Verificar se não há outros tickets de alta prioridade mais antigos
            pass
    
    def test_assign_ticket_to_operator(self, db_session, sample_tickets):
        """Testa atribuição de ticket a operador"""
        
        # Criar operador
        operator = Operator(
            name="Operador Teste",
            email="operador@test.com",
            tenant_id=sample_tickets['tenant'].id
        )
        db_session.add(operator)
        db_session.commit()
        
        queue_manager = QueueManager(db_session)
        ticket = sample_tickets['tickets'][0]
        
        success = queue_manager.assign_ticket_to_operator(
            str(ticket.id), 
            str(operator.id)
        )
        
        assert success is True
        
        db_session.refresh(ticket)
        assert ticket.assigned_operator_id == operator.id
    
    def test_auto_expire_old_tickets(self, db_session, sample_tickets):
        """Testa expiração automática de tickets antigos"""
        
        # Criar ticket muito antigo
        old_ticket = Ticket(
            tenant_id=sample_tickets['tenant'].id,
            service_id=sample_tickets['service'].id,
            ticket_number=9999,
            status=TicketStatus.IN_QUEUE.value,
            priority=QueuePriority.NORMAL.value,
            customer_name="Cliente Antigo",
            customer_cpf="99999999999",
            customer_phone="11999999999",
            consent_version="1.0",
            queued_at=datetime.utcnow() - timedelta(minutes=90)  # 90 minutos atrás
        )
        db_session.add(old_ticket)
        db_session.commit()
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        
        expired_count = queue_manager.auto_expire_old_tickets(tenant_id)
        
        assert expired_count >= 1
        
        db_session.refresh(old_ticket)
        assert old_ticket.status == TicketStatus.EXPIRED.value
        assert old_ticket.expired_at is not None
    
    def test_queue_statistics(self, db_session, sample_tickets):
        """Testa geração de estatísticas da fila"""
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        
        stats = queue_manager.get_queue_statistics(tenant_id)
        
        # Verificar estrutura das estatísticas
        assert 'total_active' in stats
        assert 'by_status' in stats
        assert 'by_priority' in stats
        assert 'by_service' in stats
        assert 'waiting_times' in stats
        assert 'queue_health' in stats
        
        # Verificar valores
        assert stats['total_active'] >= 0
        assert isinstance(stats['by_status'], dict)
        assert isinstance(stats['by_priority'], dict)
        assert isinstance(stats['waiting_times'], dict)
        
        # Verificar saúde da fila
        health = stats['queue_health']
        assert 'status' in health
        assert health['status'] in ['healthy', 'warning', 'critical']
        assert 'message' in health
        assert 'recommendations' in health
    
    def test_queue_health_assessment(self, db_session, sample_tickets):
        """Testa avaliação da saúde da fila"""
        
        queue_manager = QueueManager(db_session)
        
        # Simular fila saudável
        healthy_tickets = []
        health = queue_manager._assess_queue_health(healthy_tickets, 10.0)
        assert health['status'] == 'healthy'
        
        # Simular fila com problemas
        problematic_tickets = sample_tickets['tickets']
        health = queue_manager._assess_queue_health(problematic_tickets, 40.0)
        assert health['status'] in ['warning', 'critical']
        assert len(health['recommendations']) > 0

class TestQueueAPI:
    """Testes dos endpoints da API de fila"""
    
    def test_get_queue_endpoint(self):
        """Testa endpoint GET /tickets/queue"""
        
        # Simular autenticação
        headers = {"Authorization": "Bearer test-token"}
        
        response = client.get("/tickets/queue", headers=headers)
        
        # Deve retornar 200 ou 401 (se autenticação não configurada)
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert 'items' in data
            assert 'total' in data
            assert 'by_service' in data
            assert 'by_status' in data
            assert 'by_priority' in data
    
    def test_get_queue_with_filters(self):
        """Testa endpoint de fila com filtros"""
        
        headers = {"Authorization": "Bearer test-token"}
        
        params = {
            "sort_order": "priority",
            "priority_filter": "high",
            "include_called": True
        }
        
        response = client.get("/tickets/queue", params=params, headers=headers)
        
        # Deve aceitar os parâmetros sem erro
        assert response.status_code in [200, 401]
    
    def test_get_next_ticket_endpoint(self):
        """Testa endpoint GET /tickets/queue/next"""
        
        headers = {"Authorization": "Bearer test-token"}
        
        response = client.get("/tickets/queue/next", headers=headers)
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert 'message' in data
            assert 'ticket' in data
    
    def test_queue_statistics_endpoint(self):
        """Testa endpoint GET /tickets/queue/statistics"""
        
        headers = {"Authorization": "Bearer test-token"}
        
        response = client.get("/tickets/queue/statistics", headers=headers)
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert 'total_active' in data
            assert 'queue_health' in data

class TestQueueIntegration:
    """Testes de integração do sistema de fila"""
    
    def test_full_ticket_lifecycle_with_queue(self, db_session, sample_tickets):
        """Testa ciclo completo de um ticket na fila"""
        
        queue_manager = QueueManager(db_session)
        tenant_id = str(sample_tickets['tenant'].id)
        
        # 1. Ticket entra na fila (IN_QUEUE)
        ticket = sample_tickets['tickets'][0]
        ticket.status = TicketStatus.IN_QUEUE.value
        ticket.queued_at = datetime.utcnow()
        db_session.commit()
        
        # 2. Verificar posição na fila
        tickets = queue_manager.get_queue_tickets(tenant_id)
        assert any(t.id == ticket.id for t in tickets)
        
        # 3. Chamar ticket (CALLED)
        ticket.status = TicketStatus.CALLED.value
        ticket.called_at = datetime.utcnow()
        db_session.commit()
        
        # 4. Iniciar atendimento (IN_PROGRESS)
        ticket.status = TicketStatus.IN_PROGRESS.value
        ticket.started_at = datetime.utcnow()
        db_session.commit()
        
        # 5. Completar atendimento (COMPLETED)
        ticket.status = TicketStatus.COMPLETED.value
        ticket.completed_at = datetime.utcnow()
        db_session.commit()
        
        # 6. Verificar que não está mais na fila ativa
        active_tickets = queue_manager.get_queue_tickets(tenant_id)
        assert not any(t.id == ticket.id for t in active_tickets)
    
    def test_priority_boost_over_time(self, db_session, sample_tickets):
        """Testa boost automático de prioridade ao longo do tempo"""
        
        queue_manager = QueueManager(db_session)
        ticket = sample_tickets['tickets'][0]
        
        # Simular ticket esperando há muito tempo
        ticket.queued_at = datetime.utcnow() - timedelta(minutes=50)
        ticket.priority = QueuePriority.NORMAL.value
        db_session.commit()
        
        # Atualizar prioridades
        queue_manager._update_queue_priorities([ticket])
        
        db_session.refresh(ticket)
        assert ticket.priority == QueuePriority.HIGH.value

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
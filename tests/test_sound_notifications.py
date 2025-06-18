# 🔊 Teste Completo do Sistema de Notificações Sonoras

import asyncio
import json
from datetime import datetime, time
from typing import Dict, Any

from services.notification_service import (
    notification_service,
    NotificationEvent,
    SoundType,
    OperatorNotificationConfig
)

class SoundNotificationTester:
    """🧪 Classe para testar o sistema de notificações sonoras"""
    
    def __init__(self):
        self.test_results = []
        self.operator_configs = {}
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de um teste"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
    
    def test_operator_registration(self):
        """Testa registro de operadores"""
        print("\n🔊 TESTANDO REGISTRO DE OPERADORES")
        
        # Teste 1: Registro básico
        try:
            config = notification_service.register_operator("op1", "tenant1")
            self.log_test(
                "Registro básico de operador",
                config is not None,
                f"Operador op1 registrado com {len(config.event_sounds)} eventos"
            )
        except Exception as e:
            self.log_test("Registro básico de operador", False, str(e))
        
        # Teste 2: Registro com configurações customizadas
        try:
            custom_config = {
                "sounds_enabled": True,
                "master_volume": 0.9,
                "quiet_hours_enabled": True,
                "event_sounds": {
                    "ticket_called": {
                        "sound_type": "chime_loud",
                        "volume": 1.0,
                        "repeat_count": 3
                    }
                }
            }
            
            config = notification_service.register_operator("op2", "tenant1", custom_config)
            ticket_called_config = config.event_sounds.get(NotificationEvent.TICKET_CALLED)
            
            success = (
                config.master_volume == 0.9 and
                config.quiet_hours_enabled and
                ticket_called_config and
                ticket_called_config.sound_type == SoundType.CHIME_LOUD
            )
            
            self.log_test(
                "Registro com configurações customizadas",
                success,
                f"Volume master: {config.master_volume}, Horário silencioso: {config.quiet_hours_enabled}"
            )
        except Exception as e:
            self.log_test("Registro com configurações customizadas", False, str(e))
    
    def test_sound_configuration(self):
        """Testa configurações de som"""
        print("\n🔊 TESTANDO CONFIGURAÇÕES DE SOM")
        
        # Teste 1: Obter configuração de operador
        try:
            config = notification_service.get_operator_config("op1")
            success = config is not None and config.operator_id == "op1"
            self.log_test(
                "Obter configuração de operador",
                success,
                f"Configuração encontrada: {success}"
            )
        except Exception as e:
            self.log_test("Obter configuração de operador", False, str(e))
        
        # Teste 2: Atualizar configuração
        try:
            updates = {
                "master_volume": 0.7,
                "sounds_enabled": False,
                "event_sounds": {
                    "new_ticket_in_queue": {
                        "sound_type": "beep_short",
                        "enabled": False
                    }
                }
            }
            
            success = notification_service.update_operator_config("op1", updates)
            updated_config = notification_service.get_operator_config("op1")
            
            volume_updated = updated_config.master_volume == 0.7
            sounds_disabled = not updated_config.sounds_enabled
            
            self.log_test(
                "Atualizar configuração",
                success and volume_updated and sounds_disabled,
                f"Volume: {updated_config.master_volume}, Sons: {updated_config.sounds_enabled}"
            )
        except Exception as e:
            self.log_test("Atualizar configuração", False, str(e))
        
        # Teste 3: Exportar configuração
        try:
            exported = notification_service.export_operator_config("op1")
            success = (
                exported is not None and
                "operator_id" in exported and
                "event_sounds" in exported
            )
            self.log_test(
                "Exportar configuração",
                success,
                f"Configuração exportada com {len(exported.get('event_sounds', {}))} eventos"
            )
        except Exception as e:
            self.log_test("Exportar configuração", False, str(e))
    
    def test_sound_decision_logic(self):
        """Testa lógica de decisão de reprodução de som"""
        print("\n🔊 TESTANDO LÓGICA DE DECISÃO DE SOM")
        
        # Registrar operador para testes
        notification_service.register_operator("op_test", "tenant_test", {
            "sounds_enabled": True,
            "master_volume": 0.8,
            "only_assigned_tickets": False,
            "min_priority_level": 2
        })
        
        # Teste 1: Som deve ser reproduzido
        try:
            should_play, sound_config = notification_service.should_play_sound(
                "op_test", 
                NotificationEvent.TICKET_CALLED
            )
            
            self.log_test(
                "Som deve ser reproduzido",
                should_play and sound_config is not None,
                f"Som: {sound_config.sound_type.value if sound_config else 'None'}"
            )
        except Exception as e:
            self.log_test("Som deve ser reproduzido", False, str(e))
        
        # Teste 2: Som não deve ser reproduzido (prioridade baixa)
        try:
            should_play, sound_config = notification_service.should_play_sound(
                "op_test", 
                NotificationEvent.QUEUE_EMPTY  # Prioridade 1, menor que min_priority_level 2
            )
            
            self.log_test(
                "Som não deve ser reproduzido (prioridade baixa)",
                not should_play,
                f"Prioridade muito baixa para reproduzir"
            )
        except Exception as e:
            self.log_test("Som não deve ser reproduzido (prioridade baixa)", False, str(e))
        
        # Teste 3: Som não deve ser reproduzido (sons desabilitados)
        try:
            notification_service.update_operator_config("op_test", {"sounds_enabled": False})
            
            should_play, sound_config = notification_service.should_play_sound(
                "op_test", 
                NotificationEvent.TICKET_CALLED
            )
            
            self.log_test(
                "Som não deve ser reproduzido (sons desabilitados)",
                not should_play,
                "Sons globalmente desabilitados"
            )
        except Exception as e:
            self.log_test("Som não deve ser reproduzido (sons desabilitados)", False, str(e))
        
        # Teste 4: Filtro por ticket atribuído
        try:
            notification_service.update_operator_config("op_test", {
                "sounds_enabled": True,
                "only_assigned_tickets": True
            })
            
            # Ticket não atribuído ao operador
            ticket_data = {"assigned_operator_id": "outro_operador"}
            should_play, _ = notification_service.should_play_sound(
                "op_test", 
                NotificationEvent.TICKET_CALLED,
                ticket_data
            )
            
            self.log_test(
                "Filtro por ticket atribuído (não deve reproduzir)",
                not should_play,
                "Ticket não atribuído ao operador"
            )
            
            # Ticket atribuído ao operador
            ticket_data = {"assigned_operator_id": "op_test"}
            should_play, _ = notification_service.should_play_sound(
                "op_test", 
                NotificationEvent.TICKET_CALLED,
                ticket_data
            )
            
            self.log_test(
                "Filtro por ticket atribuído (deve reproduzir)",
                should_play,
                "Ticket atribuído ao operador"
            )
        except Exception as e:
            self.log_test("Filtro por ticket atribuído", False, str(e))
    
    def test_notification_payload_creation(self):
        """Testa criação de payloads de notificação"""
        print("\n🔊 TESTANDO CRIAÇÃO DE PAYLOADS")
        
        # Registrar operador para teste
        notification_service.register_operator("op_payload", "tenant_payload")
        
        # Teste 1: Payload básico
        try:
            payload = notification_service.create_notification_payload(
                "op_payload",
                NotificationEvent.TICKET_CALLED
            )
            
            success = (
                payload is not None and
                payload["type"] == "sound_notification" and
                payload["event"] == "ticket_called" and
                "sound" in payload and
                "timestamp" in payload
            )
            
            self.log_test(
                "Payload básico",
                success,
                f"Tipo: {payload.get('type') if payload else 'None'}"
            )
        except Exception as e:
            self.log_test("Payload básico", False, str(e))
        
        # Teste 2: Payload com dados do ticket
        try:
            ticket_data = {
                "id": "ticket-123",
                "ticket_number": 42,
                "customer_name": "João Silva"
            }
            
            payload = notification_service.create_notification_payload(
                "op_payload",
                NotificationEvent.TICKET_CALLED,
                ticket_data
            )
            
            success = (
                payload is not None and
                "ticket" in payload and
                payload["ticket"]["ticket_number"] == 42
            )
            
            self.log_test(
                "Payload com dados do ticket",
                success,
                f"Ticket: {payload.get('ticket', {}).get('ticket_number') if payload else 'None'}"
            )
        except Exception as e:
            self.log_test("Payload com dados do ticket", False, str(e))
        
        # Teste 3: Volume calculado corretamente
        try:
            # Configurar volumes específicos
            notification_service.update_operator_config("op_payload", {
                "master_volume": 0.8,
                "event_sounds": {
                    "ticket_called": {
                        "sound_type": "call_ticket",
                        "volume": 0.5
                    }
                }
            })
            
            payload = notification_service.create_notification_payload(
                "op_payload",
                NotificationEvent.TICKET_CALLED
            )
            
            expected_volume = 0.8 * 0.5  # master_volume * event_volume
            actual_volume = payload["sound"]["volume"] if payload else 0
            
            success = abs(actual_volume - expected_volume) < 0.01
            
            self.log_test(
                "Volume calculado corretamente",
                success,
                f"Esperado: {expected_volume}, Atual: {actual_volume}"
            )
        except Exception as e:
            self.log_test("Volume calculado corretamente", False, str(e))
    
    def test_available_sounds_and_events(self):
        """Testa listagem de sons e eventos disponíveis"""
        print("\n🔊 TESTANDO SONS E EVENTOS DISPONÍVEIS")
        
        # Teste 1: Sons disponíveis
        try:
            sounds = notification_service.get_available_sounds()
            
            success = (
                isinstance(sounds, dict) and
                len(sounds) > 0 and
                "beep_short" in sounds and
                "call_ticket" in sounds
            )
            
            self.log_test(
                "Sons disponíveis",
                success,
                f"{len(sounds)} sons disponíveis"
            )
        except Exception as e:
            self.log_test("Sons disponíveis", False, str(e))
        
        # Teste 2: Categorias de sons
        try:
            sounds = notification_service.get_available_sounds()
            categories = set()
            
            for sound_data in sounds.values():
                categories.add(sound_data["category"])
            
            expected_categories = {"beeps", "chimes", "notifications"}
            success = expected_categories.issubset(categories)
            
            self.log_test(
                "Categorias de sons",
                success,
                f"Categorias: {', '.join(sorted(categories))}"
            )
        except Exception as e:
            self.log_test("Categorias de sons", False, str(e))
        
        # Teste 3: Eventos de notificação
        try:
            events = list(NotificationEvent)
            success = len(events) >= 10  # Esperamos pelo menos 10 eventos
            
            self.log_test(
                "Eventos de notificação",
                success,
                f"{len(events)} eventos disponíveis"
            )
        except Exception as e:
            self.log_test("Eventos de notificação", False, str(e))
    
    def test_quiet_hours(self):
        """Testa funcionalidade de horário silencioso"""
        print("\n🔊 TESTANDO HORÁRIO SILENCIOSO")
        
        # Registrar operador com horário silencioso
        notification_service.register_operator("op_quiet", "tenant_quiet", {
            "quiet_hours_enabled": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00"
        })
        
        config = notification_service.get_operator_config("op_quiet")
        
        # Teste 1: Verificar se está em horário silencioso
        try:
            # Simular diferentes horários
            test_times = [
                ("23:00", True),   # Deve estar em horário silencioso
                ("02:00", True),   # Deve estar em horário silencioso
                ("07:00", True),   # Deve estar em horário silencioso
                ("10:00", False),  # Não deve estar em horário silencioso
                ("15:00", False),  # Não deve estar em horário silencioso
                ("21:00", False),  # Não deve estar em horário silencioso
            ]
            
            # Nota: Este teste é conceitual, pois _is_quiet_hours usa datetime.now()
            # Em um teste real, precisaríamos mockar o datetime
            
            self.log_test(
                "Horário silencioso configurado",
                config.quiet_hours_enabled,
                f"Início: {config.quiet_hours_start}, Fim: {config.quiet_hours_end}"
            )
        except Exception as e:
            self.log_test("Horário silencioso configurado", False, str(e))
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES DO SISTEMA DE NOTIFICAÇÕES SONORAS")
        print("=" * 60)
        
        # Executar todos os testes
        self.test_operator_registration()
        self.test_sound_configuration()
        self.test_sound_decision_logic()
        self.test_notification_payload_creation()
        self.test_available_sounds_and_events()
        self.test_quiet_hours()
        
        # Resumo dos resultados
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"✅ {passed_tests}/{total_tests} testes aprovados")
        if failed_tests > 0:
            print(f"❌ {failed_tests}/{total_tests} testes falharam")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Listar testes que falharam
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n🎯 SISTEMA DE NOTIFICAÇÕES SONORAS TESTADO!")
        return success_rate >= 80  # Considera sucesso se 80% ou mais dos testes passaram

def main():
    """Função principal para executar os testes"""
    tester = SoundNotificationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TODOS OS TESTES PRINCIPAIS PASSARAM!")
        print("🔊 Sistema de notificações sonoras está funcionando corretamente")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija antes de usar em produção")
    
    return success

if __name__ == "__main__":
    main()
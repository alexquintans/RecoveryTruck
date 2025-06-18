# 🎛️ Gerenciador Central de Terminais Físicos

import asyncio
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

from .terminal import (
    TerminalAdapter, TerminalStatus, PaymentMethod, TransactionStatus,
    TransactionRequest, TransactionResponse, PaymentTerminalError,
    TerminalAdapterFactory
)

logger = logging.getLogger(__name__)

class TerminalManager:
    """Gerenciador central para terminais físicos"""
    
    def __init__(self):
        self._terminals: Dict[str, TerminalAdapter] = {}
        self._terminal_configs: Dict[str, Dict[str, Any]] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._health_check_interval = 30  # segundos
        
        logger.info("🎛️ Terminal Manager initialized")
    
    async def initialize(self, tenant_configs: Dict[str, Dict[str, Any]]):
        """Inicializa terminais para todos os tenants"""
        logger.info(f"🚀 Initializing terminals for {len(tenant_configs)} tenants")
        
        for tenant_id, config in tenant_configs.items():
            try:
                await self.add_terminal(tenant_id, config)
            except Exception as e:
                logger.error(f"❌ Failed to initialize terminal for tenant {tenant_id}: {e}")
        
        # Inicia monitoramento de saúde
        await self.start_health_monitoring()
        
        logger.info(f"✅ Terminal Manager initialized with {len(self._terminals)} terminals")
    
    async def add_terminal(self, tenant_id: str, config: Dict[str, Any]) -> bool:
        """Adiciona terminal para um tenant"""
        try:
            logger.info(f"➕ Adding terminal for tenant {tenant_id}")
            
            # Cria adaptador do terminal
            terminal = TerminalAdapterFactory.create_from_tenant_config(tenant_id, config)
            
            if not terminal:
                logger.warning(f"⚠️ No terminal created for tenant {tenant_id}")
                return False
            
            # Adiciona callbacks de status
            terminal.add_status_callback(self._on_terminal_status_change)
            
            # Armazena terminal e configuração
            self._terminals[tenant_id] = terminal
            self._terminal_configs[tenant_id] = config
            
            # Tenta conectar automaticamente
            try:
                await terminal.connect()
                logger.info(f"✅ Terminal connected for tenant {tenant_id}")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-connect terminal for tenant {tenant_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding terminal for tenant {tenant_id}: {e}")
            return False
    
    async def remove_terminal(self, tenant_id: str) -> bool:
        """Remove terminal de um tenant"""
        if tenant_id not in self._terminals:
            return False
        
        try:
            logger.info(f"➖ Removing terminal for tenant {tenant_id}")
            
            terminal = self._terminals[tenant_id]
            
            # Desconecta terminal
            await terminal.disconnect()
            
            # Remove callbacks
            terminal.remove_status_callback(self._on_terminal_status_change)
            
            # Remove do registro
            del self._terminals[tenant_id]
            del self._terminal_configs[tenant_id]
            
            logger.info(f"✅ Terminal removed for tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error removing terminal for tenant {tenant_id}: {e}")
            return False
    
    def get_terminal(self, tenant_id: str) -> Optional[TerminalAdapter]:
        """Obtém terminal de um tenant"""
        return self._terminals.get(tenant_id)
    
    async def get_terminal_status(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status detalhado do terminal"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            return None
        
        try:
            health = await terminal.health_check()
            return {
                "tenant_id": tenant_id,
                "terminal_type": terminal.config.get("type"),
                "status": terminal.status.value,
                "health": health,
                "current_transaction": terminal.current_transaction.__dict__ if terminal.current_transaction else None
            }
        except Exception as e:
            logger.error(f"❌ Error getting terminal status for {tenant_id}: {e}")
            return {
                "tenant_id": tenant_id,
                "status": "error",
                "error": str(e)
            }
    
    async def list_terminals(self) -> List[Dict[str, Any]]:
        """Lista todos os terminais e seus status"""
        terminals = []
        
        for tenant_id in self._terminals.keys():
            status = await self.get_terminal_status(tenant_id)
            if status:
                terminals.append(status)
        
        return terminals
    
    # === Métodos de Transação ===
    
    async def start_transaction(self, tenant_id: str, request: TransactionRequest) -> str:
        """Inicia transação em terminal específico"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            raise PaymentTerminalError(f"No terminal found for tenant {tenant_id}")
        
        logger.info(f"💳 Starting transaction for tenant {tenant_id}: R$ {request.amount:.2f}")
        
        try:
            # Verifica se terminal está conectado
            if not await terminal.is_connected():
                logger.info(f"🔌 Terminal not connected, attempting to connect...")
                if not await terminal.connect():
                    raise PaymentTerminalError("Could not connect to terminal")
            
            # Inicia transação
            transaction_id = await terminal.start_transaction(request)
            
            logger.info(f"✅ Transaction started: {transaction_id}")
            return transaction_id
            
        except Exception as e:
            logger.error(f"❌ Error starting transaction for tenant {tenant_id}: {e}")
            raise
    
    async def get_transaction_status(self, tenant_id: str, transaction_id: str) -> TransactionResponse:
        """Obtém status de transação"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            raise PaymentTerminalError(f"No terminal found for tenant {tenant_id}")
        
        return await terminal.get_transaction_status(transaction_id)
    
    async def cancel_transaction(self, tenant_id: str, transaction_id: str) -> bool:
        """Cancela transação"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            return False
        
        return await terminal.cancel_transaction(transaction_id)
    
    async def print_receipt(self, tenant_id: str, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Imprime comprovante"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            return False
        
        return await terminal.print_receipt(transaction_id, receipt_type)
    
    # === Métodos de Gerenciamento ===
    
    async def connect_terminal(self, tenant_id: str) -> bool:
        """Conecta terminal específico"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            return False
        
        try:
            return await terminal.connect()
        except Exception as e:
            logger.error(f"❌ Error connecting terminal for {tenant_id}: {e}")
            return False
    
    async def disconnect_terminal(self, tenant_id: str) -> bool:
        """Desconecta terminal específico"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            return False
        
        try:
            return await terminal.disconnect()
        except Exception as e:
            logger.error(f"❌ Error disconnecting terminal for {tenant_id}: {e}")
            return False
    
    async def reset_terminal(self, tenant_id: str) -> bool:
        """Reseta terminal específico"""
        terminal = self.get_terminal(tenant_id)
        if not terminal:
            return False
        
        try:
            return await terminal.reset_terminal()
        except Exception as e:
            logger.error(f"❌ Error resetting terminal for {tenant_id}: {e}")
            return False
    
    # === Monitoramento de Saúde ===
    
    async def start_health_monitoring(self):
        """Inicia monitoramento automático de saúde"""
        if self._health_check_task and not self._health_check_task.done():
            return
        
        logger.info("🏥 Starting terminal health monitoring")
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def stop_health_monitoring(self):
        """Para monitoramento de saúde"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            
            logger.info("🏥 Terminal health monitoring stopped")
    
    async def _health_check_loop(self):
        """Loop de verificação de saúde"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in health check loop: {e}")
                await asyncio.sleep(5)  # Pausa menor em caso de erro
    
    async def _perform_health_checks(self):
        """Executa verificações de saúde em todos os terminais"""
        for tenant_id, terminal in self._terminals.items():
            try:
                health = await terminal.health_check()
                
                # Log apenas se houver mudança significativa
                if not health.get("connected") and terminal.status != TerminalStatus.DISCONNECTED:
                    logger.warning(f"⚠️ Terminal {tenant_id} appears disconnected")
                
                # Tenta reconectar terminais com erro
                if terminal.status == TerminalStatus.ERROR:
                    logger.info(f"🔄 Attempting to reconnect terminal {tenant_id}")
                    await terminal.reset_terminal()
                
            except Exception as e:
                logger.error(f"❌ Health check failed for terminal {tenant_id}: {e}")
    
    async def _on_terminal_status_change(self, old_status: TerminalStatus, new_status: TerminalStatus, terminal: TerminalAdapter):
        """Callback para mudanças de status de terminal"""
        tenant_id = None
        
        # Encontra tenant_id do terminal
        for tid, t in self._terminals.items():
            if t == terminal:
                tenant_id = tid
                break
        
        if tenant_id:
            logger.info(f"🔄 Terminal {tenant_id} status: {old_status.value} → {new_status.value}")
            
            # Ações automáticas baseadas no status
            if new_status == TerminalStatus.ERROR:
                logger.warning(f"⚠️ Terminal {tenant_id} entered error state")
                # Poderia enviar notificação, tentar reconectar, etc.
            
            elif new_status == TerminalStatus.CONNECTED and old_status in [TerminalStatus.ERROR, TerminalStatus.DISCONNECTED]:
                logger.info(f"✅ Terminal {tenant_id} recovered and connected")
    
    # === Métodos de Limpeza ===
    
    async def shutdown(self):
        """Encerra gerenciador e desconecta todos os terminais"""
        logger.info("🛑 Shutting down Terminal Manager")
        
        # Para monitoramento
        await self.stop_health_monitoring()
        
        # Desconecta todos os terminais
        disconnect_tasks = []
        for tenant_id in list(self._terminals.keys()):
            task = asyncio.create_task(self.remove_terminal(tenant_id))
            disconnect_tasks.append(task)
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        logger.info("✅ Terminal Manager shutdown complete")
    
    # === Métodos de Estatísticas ===
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos terminais"""
        total = len(self._terminals)
        connected = sum(1 for t in self._terminals.values() if t.status == TerminalStatus.CONNECTED)
        busy = sum(1 for t in self._terminals.values() if t.status == TerminalStatus.BUSY)
        error = sum(1 for t in self._terminals.values() if t.status == TerminalStatus.ERROR)
        
        return {
            "total_terminals": total,
            "connected": connected,
            "busy": busy,
            "error": error,
            "disconnected": total - connected - busy - error,
            "health_check_interval": self._health_check_interval,
            "monitoring_active": self._health_check_task is not None and not self._health_check_task.done()
        }

# Instância global do gerenciador
terminal_manager = TerminalManager() 
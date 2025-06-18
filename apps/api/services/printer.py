from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import logging
from escpos.printer import Usb, Network, Serial
from escpos.exceptions import Error as ESCPOSError

logger = logging.getLogger(__name__)

class MockPrinter:
    """Impressora mock para desenvolvimento e testes"""
    def set(self, **kwargs):
        pass
    
    def text(self, text: str):
        print(f"[MOCK PRINTER] {text.strip()}")
    
    def cut(self):
        print("[MOCK PRINTER] --- PAPEL CORTADO ---")

class PrinterService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.printer = None
        self.is_mock = config.get("type") == "mock"
        self.initialize_printer()

    def initialize_printer(self):
        """Inicializa a impressora com base na configuração"""
        try:
            if self.config["type"] == "mock":
                # Impressora mock para desenvolvimento
                self.printer = MockPrinter()
                logger.info("Mock printer initialized for development")
                return
                
            elif self.config["type"] == "usb":
                self.printer = Usb(
                    idVendor=self.config["vendor_id"],
                    idProduct=self.config["product_id"],
                    in_ep=self.config.get("in_ep", 0x81),
                    out_ep=self.config.get("out_ep", 0x03)
                )
            elif self.config["type"] == "network":
                self.printer = Network(
                    host=self.config["host"],
                    port=self.config.get("port", 9100)
                )
            elif self.config["type"] == "serial":
                self.printer = Serial(
                    devfile=self.config["serial_port"],
                    baudrate=self.config.get("baudrate", 9600)
                )
            else:
                raise ValueError(f"Unsupported printer type: {self.config['type']}")
            
            logger.info(f"Real printer initialized: {self.config['type']}")
            
        except Exception as e:
            logger.error(f"Error initializing printer: {str(e)}")
            # Fallback para mock em caso de erro
            logger.warning("Falling back to mock printer")
            self.printer = MockPrinter()
            self.is_mock = True

    async def print_ticket(self, ticket_data: Dict[str, Any]):
        """Imprime um comprovante de ticket"""
        if not self.printer:
            logger.error("Printer not initialized")
            return False

        try:
            logger.info(f"🖨️ Printing ticket #{ticket_data.get('ticket_number', 'N/A')}")
            
            # Cabeçalho
            self.printer.set(align="center")
            self.printer.text("RECOVERY TRUCK\n")
            self.printer.text("COMPROVANTE DE ATENDIMENTO\n")
            self.printer.text("=" * 32 + "\n\n")

            # Dados do ticket
            self.printer.set(align="left")
            self.printer.text(f"Ticket: #{ticket_data['ticket_number']:03d}\n")
            self.printer.text(f"Data: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(f"Serviço: {ticket_data['service_name']}\n")
            self.printer.text(f"Cliente: {ticket_data['customer_name']}\n")
            
            if ticket_data.get("customer_cpf"):
                cpf_masked = f"***{ticket_data['customer_cpf']}"
                self.printer.text(f"CPF: {cpf_masked}\n")

            # Status em destaque
            self.printer.text("\n")
            self.printer.set(align="center")
            self.printer.text("⬇️ STATUS ⬇️\n")
            self.printer.text(f"** {ticket_data['status']} **\n")
            self.printer.text("\n")

            # Instruções
            self.printer.set(align="left")
            self.printer.text("INSTRUÇÕES:\n")
            self.printer.text("• Aguarde sua senha ser chamada\n")
            self.printer.text("• Mantenha este comprovante\n")
            self.printer.text("• Procure o operador em caso de dúvidas\n")

            # Rodapé
            self.printer.text("\n")
            self.printer.set(align="center")
            self.printer.text("=" * 32 + "\n")
            self.printer.text("Obrigado pela preferência!\n")
            self.printer.text("recovertruck.com.br\n")
            self.printer.text("=" * 32 + "\n\n\n")

            # Corta o papel
            self.printer.cut()
            
            logger.info(f"✅ Ticket #{ticket_data['ticket_number']} printed successfully")
            return True

        except ESCPOSError as e:
            logger.error(f"❌ ESC/POS error printing ticket: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ General error printing ticket: {str(e)}")
            return False

    async def print_payment_receipt(self, payment_data: Dict[str, Any]):
        """Imprime um comprovante de pagamento"""
        if not self.printer:
            logger.error("Printer not initialized")
            return False

        try:
            logger.info(f"🖨️ Printing payment receipt for transaction {payment_data.get('transaction_id', 'N/A')}")
            
            # Cabeçalho
            self.printer.set(align="center")
            self.printer.text("RECOVERY TRUCK\n")
            self.printer.text("COMPROVANTE DE PAGAMENTO\n")
            self.printer.text("=" * 32 + "\n\n")

            # Dados do pagamento
            self.printer.set(align="left")
            self.printer.text(f"Ticket: #{payment_data['ticket_number']:03d}\n")
            self.printer.text(f"Data: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(f"Valor: R$ {payment_data['amount']:.2f}\n")
            self.printer.text(f"Forma: {payment_data['payment_method'].upper()}\n")
            self.printer.text(f"Status: {payment_data['status'].upper()}\n")
            
            if payment_data.get("transaction_id"):
                self.printer.text(f"Transação: {payment_data['transaction_id']}\n")

            # Rodapé
            self.printer.text("\n" + "=" * 32 + "\n")
            self.printer.text("Pagamento processado com sucesso!\n")
            self.printer.text("recovertruck.com.br\n")
            self.printer.text("=" * 32 + "\n\n\n")

            # Corta o papel
            self.printer.cut()
            
            logger.info(f"✅ Payment receipt printed successfully")
            return True

        except ESCPOSError as e:
            logger.error(f"❌ ESC/POS error printing payment receipt: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ General error printing payment receipt: {str(e)}")
            return False

    async def print_error(self, error_message: str):
        """Imprime uma mensagem de erro"""
        if not self.printer:
            logger.error("Printer not initialized")
            return False

        try:
            logger.info(f"🖨️ Printing error message: {error_message}")
            
            self.printer.set(align="center")
            self.printer.text("RECOVERY TRUCK\n")
            self.printer.text("⚠️ ERRO ⚠️\n")
            self.printer.text("=" * 32 + "\n\n")
            self.printer.set(align="left")
            self.printer.text(f"{error_message}\n")
            self.printer.text("\nProcure o operador para assistência\n")
            self.printer.text("\n" + "=" * 32 + "\n\n\n")
            self.printer.cut()
            
            logger.info(f"✅ Error message printed successfully")
            return True

        except ESCPOSError as e:
            logger.error(f"❌ ESC/POS error printing error message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ General error printing error message: {str(e)}")
            return False

class PrinterManager:
    def __init__(self):
        self.printers: Dict[str, PrinterService] = {}
        self.print_queue = asyncio.Queue()
        self._print_task = None

    def add_printer(self, name: str, config: Dict[str, Any]):
        """Adiciona uma impressora ao gerenciador"""
        self.printers[name] = PrinterService(config)
        logger.info(f"📄 Printer '{name}' added with config: {config.get('type', 'unknown')}")

    async def start_print_task(self):
        """Inicia a tarefa de impressão"""
        if self._print_task is None:
            self._print_task = asyncio.create_task(self._process_print_queue())
            logger.info("🖨️ Print task started")

    async def stop_print_task(self):
        """Para a tarefa de impressão"""
        if self._print_task:
            self._print_task.cancel()
            self._print_task = None
            logger.info("🖨️ Print task stopped")

    async def _process_print_queue(self):
        """Processa a fila de impressão"""
        logger.info("🔄 Print queue processor started")
        while True:
            try:
                print_job = await self.print_queue.get()
                printer_name = print_job["printer"]
                job_type = print_job["type"]
                data = print_job["data"]

                logger.info(f"📋 Processing print job: {job_type} for printer '{printer_name}'")

                if printer_name in self.printers:
                    printer = self.printers[printer_name]
                    success = False
                    
                    if job_type == "ticket":
                        success = await printer.print_ticket(data)
                    elif job_type == "payment":
                        success = await printer.print_payment_receipt(data)
                    elif job_type == "error":
                        success = await printer.print_error(data)
                    
                    if success:
                        logger.info(f"✅ Print job completed successfully")
                    else:
                        logger.error(f"❌ Print job failed")
                else:
                    logger.error(f"❌ Printer '{printer_name}' not found")

                self.print_queue.task_done()
                
            except asyncio.CancelledError:
                logger.info("🔄 Print queue processor cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error processing print queue: {str(e)}")
                await asyncio.sleep(1)

    async def queue_print_job(self, printer_name: str, job_type: str, data: Dict[str, Any]):
        """Adiciona um job à fila de impressão"""
        await self.print_queue.put({
            "printer": printer_name,
            "type": job_type,
            "data": data
        })
        logger.info(f"📥 Print job queued: {job_type} for printer '{printer_name}'")

    def get_printer_status(self, printer_name: str) -> Dict[str, Any]:
        """Retorna o status de uma impressora"""
        if printer_name in self.printers:
            printer = self.printers[printer_name]
            return {
                "name": printer_name,
                "type": printer.config.get("type", "unknown"),
                "is_mock": printer.is_mock,
                "initialized": printer.printer is not None
            }
        return {"name": printer_name, "status": "not_found"}

# Instância global do gerenciador de impressão
printer_manager = PrinterManager() 
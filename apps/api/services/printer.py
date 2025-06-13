from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import logging
from escpos.printer import Usb, Network, Serial
from escpos.exceptions import Error as ESCPOSError

logger = logging.getLogger(__name__)

class PrinterService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.printer = None
        self.initialize_printer()

    def initialize_printer(self):
        """Inicializa a impressora com base na configuração"""
        try:
            if self.config["type"] == "usb":
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
                    devfile=self.config["port"],
                    baudrate=self.config.get("baudrate", 9600)
                )
            else:
                raise ValueError(f"Unsupported printer type: {self.config['type']}")
            
            logger.info(f"Printer initialized: {self.config['type']}")
        except Exception as e:
            logger.error(f"Error initializing printer: {str(e)}")
            self.printer = None

    async def print_ticket(self, ticket_data: Dict[str, Any]):
        """Imprime um comprovante de ticket"""
        if not self.printer:
            logger.error("Printer not initialized")
            return False

        try:
            # Cabeçalho
            self.printer.set(align="center")
            self.printer.text("COMPROVANTE DE ATENDIMENTO\n")
            self.printer.text("=" * 32 + "\n\n")

            # Dados do ticket
            self.printer.set(align="left")
            self.printer.text(f"Ticket: {ticket_data['ticket_number']}\n")
            self.printer.text(f"Data: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(f"Serviço: {ticket_data['service_name']}\n")
            self.printer.text(f"Cliente: {ticket_data['customer_name']}\n")
            
            if ticket_data.get("customer_cpf"):
                self.printer.text(f"CPF: {ticket_data['customer_cpf']}\n")

            # Status
            self.printer.text("\n")
            self.printer.set(align="center")
            self.printer.text(f"Status: {ticket_data['status'].upper()}\n")

            # Rodapé
            self.printer.text("\n" + "=" * 32 + "\n")
            self.printer.text("Obrigado pela preferência!\n")
            self.printer.text("=" * 32 + "\n\n\n")

            # Corta o papel
            self.printer.cut()
            
            logger.info(f"Ticket printed: {ticket_data['ticket_number']}")
            return True

        except ESCPOSError as e:
            logger.error(f"Error printing ticket: {str(e)}")
            return False

    async def print_payment_receipt(self, payment_data: Dict[str, Any]):
        """Imprime um comprovante de pagamento"""
        if not self.printer:
            logger.error("Printer not initialized")
            return False

        try:
            # Cabeçalho
            self.printer.set(align="center")
            self.printer.text("COMPROVANTE DE PAGAMENTO\n")
            self.printer.text("=" * 32 + "\n\n")

            # Dados do pagamento
            self.printer.set(align="left")
            self.printer.text(f"Ticket: {payment_data['ticket_number']}\n")
            self.printer.text(f"Data: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n")
            self.printer.text(f"Valor: R$ {payment_data['amount']:.2f}\n")
            self.printer.text(f"Forma: {payment_data['payment_method']}\n")
            self.printer.text(f"Status: {payment_data['status']}\n")
            
            if payment_data.get("transaction_id"):
                self.printer.text(f"Transação: {payment_data['transaction_id']}\n")

            # Rodapé
            self.printer.text("\n" + "=" * 32 + "\n")
            self.printer.text("Obrigado pela preferência!\n")
            self.printer.text("=" * 32 + "\n\n\n")

            # Corta o papel
            self.printer.cut()
            
            logger.info(f"Payment receipt printed: {payment_data['transaction_id']}")
            return True

        except ESCPOSError as e:
            logger.error(f"Error printing payment receipt: {str(e)}")
            return False

    async def print_error(self, error_message: str):
        """Imprime uma mensagem de erro"""
        if not self.printer:
            logger.error("Printer not initialized")
            return False

        try:
            self.printer.set(align="center")
            self.printer.text("ERRO\n")
            self.printer.text("=" * 32 + "\n\n")
            self.printer.text(f"{error_message}\n")
            self.printer.text("\n" + "=" * 32 + "\n\n\n")
            self.printer.cut()
            
            logger.info(f"Error message printed: {error_message}")
            return True

        except ESCPOSError as e:
            logger.error(f"Error printing error message: {str(e)}")
            return False

class PrinterManager:
    def __init__(self):
        self.printers: Dict[str, PrinterService] = {}
        self.print_queue = asyncio.Queue()
        self._print_task = None

    def add_printer(self, name: str, config: Dict[str, Any]):
        """Adiciona uma impressora ao gerenciador"""
        self.printers[name] = PrinterService(config)
        logger.info(f"Printer added: {name}")

    async def start_print_task(self):
        """Inicia a tarefa de impressão"""
        if self._print_task is None:
            self._print_task = asyncio.create_task(self._process_print_queue())

    async def stop_print_task(self):
        """Para a tarefa de impressão"""
        if self._print_task:
            self._print_task.cancel()
            self._print_task = None

    async def _process_print_queue(self):
        """Processa a fila de impressão"""
        while True:
            try:
                print_job = await self.print_queue.get()
                printer_name = print_job["printer"]
                job_type = print_job["type"]
                data = print_job["data"]

                if printer_name in self.printers:
                    printer = self.printers[printer_name]
                    if job_type == "ticket":
                        await printer.print_ticket(data)
                    elif job_type == "payment":
                        await printer.print_payment_receipt(data)
                    elif job_type == "error":
                        await printer.print_error(data)

                self.print_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing print queue: {str(e)}")
                await asyncio.sleep(1)

    async def queue_print_job(self, printer_name: str, job_type: str, data: Dict[str, Any]):
        """Adiciona um job à fila de impressão"""
        await self.print_queue.put({
            "printer": printer_name,
            "type": job_type,
            "data": data
        })
        logger.info(f"Print job queued: {job_type} for {printer_name}")

# Instância global do gerenciador de impressão
printer_manager = PrinterManager() 
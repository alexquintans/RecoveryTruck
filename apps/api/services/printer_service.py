# 🖨️ Serviço Completo de Impressão para Comprovantes

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from pathlib import Path

# Imports para diferentes tipos de impressora
try:
    import win32print
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import cups
    CUPS_AVAILABLE = True
except ImportError:
    CUPS_AVAILABLE = False

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import socket
    SOCKET_AVAILABLE = True
except ImportError:
    SOCKET_AVAILABLE = False

logger = logging.getLogger(__name__)

class PrinterType(Enum):
    """Tipos de impressora suportados"""
    THERMAL = "thermal"          # Impressora térmica (comum em PDVs)
    LASER = "laser"              # Impressora laser/jato de tinta
    MATRIX = "matrix"            # Impressora matricial
    VIRTUAL = "virtual"          # Impressora virtual (PDF/arquivo)
    NETWORK = "network"          # Impressora de rede
    USB = "usb"                  # Impressora USB
    SERIAL = "serial"            # Impressora serial

class PrinterConnection(Enum):
    """Tipos de conexão com impressora"""
    WINDOWS_DRIVER = "windows_driver"  # Driver Windows
    CUPS = "cups"                      # CUPS (Linux/Mac)
    SERIAL = "serial"                  # Porta serial
    NETWORK = "network"                # Rede (TCP/IP)
    USB_RAW = "usb_raw"               # USB direto
    FILE = "file"                      # Arquivo

class ReceiptType(Enum):
    """Tipos de comprovante"""
    CUSTOMER = "customer"        # Via do cliente
    MERCHANT = "merchant"        # Via do estabelecimento
    BOTH = "both"               # Ambas as vias
    SUMMARY = "summary"         # Resumo da transação

@dataclass
class PrinterConfig:
    """Configuração de impressora"""
    name: str
    printer_type: PrinterType
    connection_type: PrinterConnection
    
    # Configurações de conexão
    port: Optional[str] = None              # COM1, /dev/ttyUSB0, etc.
    ip_address: Optional[str] = None        # Para impressoras de rede
    tcp_port: int = 9100                    # Porta TCP padrão
    baudrate: int = 9600                    # Para conexão serial
    
    # Configurações de impressão
    paper_width: int = 80                   # Largura do papel (mm)
    chars_per_line: int = 48               # Caracteres por linha
    font_size: str = "normal"              # normal, small, large
    encoding: str = "cp850"                # Codificação de caracteres
    
    # Configurações específicas
    cut_paper: bool = True                 # Cortar papel após impressão
    open_drawer: bool = False              # Abrir gaveta
    beep: bool = False                     # Emitir beep
    
    # Timeouts
    connection_timeout: int = 5            # Timeout de conexão (segundos)
    print_timeout: int = 30                # Timeout de impressão (segundos)

@dataclass
class ReceiptData:
    """Dados do comprovante"""
    transaction_id: str
    receipt_type: ReceiptType
    
    # Dados da transação
    amount: float
    payment_method: str
    status: str
    timestamp: datetime
    
    # Dados do estabelecimento
    merchant_name: str
    merchant_cnpj: str
    merchant_address: Optional[str] = None
    
    # Dados do cliente
    customer_name: Optional[str] = None
    customer_cpf: Optional[str] = None
    
    # Dados específicos por modalidade
    card_brand: Optional[str] = None
    card_last_digits: Optional[str] = None
    installments: Optional[int] = None
    authorization_code: Optional[str] = None
    nsu: Optional[str] = None
    
    # PIX
    pix_key: Optional[str] = None
    pix_qr_code: Optional[str] = None
    
    # Boleto
    boleto_barcode: Optional[str] = None
    boleto_due_date: Optional[datetime] = None
    
    # Dados adicionais
    metadata: Dict[str, Any] = field(default_factory=dict)

class PrinterService:
    """🖨️ Serviço completo de impressão"""
    
    def __init__(self):
        self._printers: Dict[str, PrinterConfig] = {}
        self._default_printer: Optional[str] = None
        logger.info("🖨️ PrinterService initialized")
    
    def register_printer(self, printer_id: str, config: PrinterConfig):
        """Registra uma nova impressora"""
        self._printers[printer_id] = config
        
        if not self._default_printer:
            self._default_printer = printer_id
        
        logger.info(f"🖨️ Printer registered: {printer_id} ({config.printer_type.value})")
    
    def set_default_printer(self, printer_id: str):
        """Define impressora padrão"""
        if printer_id in self._printers:
            self._default_printer = printer_id
            logger.info(f"🖨️ Default printer set: {printer_id}")
        else:
            raise ValueError(f"Printer not found: {printer_id}")
    
    async def print_receipt(
        self,
        receipt_data: ReceiptData,
        printer_id: Optional[str] = None,
        copies: int = 1
    ) -> bool:
        """Imprime comprovante"""
        
        # Usa impressora padrão se não especificada
        if not printer_id:
            printer_id = self._default_printer
        
        if not printer_id or printer_id not in self._printers:
            logger.error(f"❌ Printer not found: {printer_id}")
            return False
        
        printer_config = self._printers[printer_id]
        
        try:
            logger.info(f"🖨️ Printing receipt {receipt_data.transaction_id} on {printer_id}")
            
            # Gera conteúdo do comprovante
            receipt_content = self._generate_receipt_content(receipt_data, printer_config)
            
            # Imprime baseado no tipo de conexão
            success = await self._print_content(receipt_content, printer_config, copies)
            
            if success:
                logger.info(f"✅ Receipt printed successfully: {receipt_data.transaction_id}")
            else:
                logger.error(f"❌ Failed to print receipt: {receipt_data.transaction_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error printing receipt {receipt_data.transaction_id}: {e}")
            return False
    
    def _generate_receipt_content(self, receipt_data: ReceiptData, config: PrinterConfig) -> str:
        """Gera conteúdo do comprovante"""
        
        lines = []
        width = config.chars_per_line
        
        # Cabeçalho
        lines.append("=" * width)
        lines.append(self._center_text("COMPROVANTE DE PAGAMENTO", width))
        lines.append("=" * width)
        lines.append("")
        
        # Dados do estabelecimento
        lines.append(self._center_text(receipt_data.merchant_name, width))
        lines.append(self._center_text(f"CNPJ: {self._format_cnpj(receipt_data.merchant_cnpj)}", width))
        if receipt_data.merchant_address:
            lines.append(self._center_text(receipt_data.merchant_address, width))
        lines.append("")
        
        # Dados da transação
        lines.append(f"Data/Hora: {receipt_data.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append(f"Transacao: {receipt_data.transaction_id}")
        lines.append(f"Valor: R$ {receipt_data.amount:.2f}")
        lines.append(f"Modalidade: {self._format_payment_method(receipt_data.payment_method)}")
        lines.append(f"Status: {self._format_status(receipt_data.status)}")
        lines.append("")
        
        # Dados específicos por modalidade
        if receipt_data.payment_method in ["credit_card", "debit_card"]:
            if receipt_data.card_brand:
                lines.append(f"Bandeira: {receipt_data.card_brand.upper()}")
            if receipt_data.card_last_digits:
                lines.append(f"Cartao: ****{receipt_data.card_last_digits}")
            if receipt_data.installments and receipt_data.installments > 1:
                lines.append(f"Parcelas: {receipt_data.installments}x")
            if receipt_data.authorization_code:
                lines.append(f"Autorizacao: {receipt_data.authorization_code}")
            if receipt_data.nsu:
                lines.append(f"NSU: {receipt_data.nsu}")
        
        elif receipt_data.payment_method == "pix":
            if receipt_data.pix_key:
                lines.append(f"Chave PIX: {receipt_data.pix_key}")
            lines.append("PIX - Pagamento instantaneo")
        
        elif receipt_data.payment_method == "boleto":
            if receipt_data.boleto_due_date:
                lines.append(f"Vencimento: {receipt_data.boleto_due_date.strftime('%d/%m/%Y')}")
            lines.append("Boleto bancario")
        
        lines.append("")
        
        # Dados do cliente (se disponível)
        if receipt_data.customer_name:
            lines.append(f"Cliente: {receipt_data.customer_name}")
        if receipt_data.customer_cpf:
            lines.append(f"CPF: {self._format_cpf(receipt_data.customer_cpf)}")
        
        if receipt_data.customer_name or receipt_data.customer_cpf:
            lines.append("")
        
        # Tipo de via
        if receipt_data.receipt_type == ReceiptType.CUSTOMER:
            lines.append(self._center_text("*** VIA DO CLIENTE ***", width))
        elif receipt_data.receipt_type == ReceiptType.MERCHANT:
            lines.append(self._center_text("*** VIA DO ESTABELECIMENTO ***", width))
        
        lines.append("")
        lines.append("=" * width)
        lines.append(self._center_text("Obrigado pela preferencia!", width))
        lines.append("=" * width)
        
        # Adiciona comandos de controle da impressora
        content = "\n".join(lines)
        
        # Comandos ESC/POS para impressoras térmicas
        if config.printer_type == PrinterType.THERMAL:
            content = self._add_thermal_commands(content, config)
        
        return content
    
    def _add_thermal_commands(self, content: str, config: PrinterConfig) -> str:
        """Adiciona comandos ESC/POS para impressoras térmicas"""
        commands = []
        
        # Inicialização
        commands.append("\x1B\x40")  # ESC @ - Inicializar impressora
        
        # Configurar fonte
        if config.font_size == "small":
            commands.append("\x1B\x4D\x01")  # ESC M - Fonte pequena
        elif config.font_size == "large":
            commands.append("\x1B\x21\x10")  # ESC ! - Fonte dupla altura
        
        # Conteúdo
        commands.append(content)
        
        # Comandos finais
        if config.beep:
            commands.append("\x1B\x42\x03\x03")  # ESC B - Beep
        
        if config.cut_paper:
            commands.append("\x1D\x56\x00")  # GS V - Cortar papel
        
        if config.open_drawer:
            commands.append("\x1B\x70\x00\x19\xFA")  # ESC p - Abrir gaveta
        
        return "".join(commands)
    
    async def _print_content(self, content: str, config: PrinterConfig, copies: int) -> bool:
        """Imprime conteúdo baseado no tipo de conexão"""
        
        for copy in range(copies):
            try:
                if config.connection_type == PrinterConnection.WINDOWS_DRIVER:
                    success = await self._print_windows_driver(content, config)
                elif config.connection_type == PrinterConnection.SERIAL:
                    success = await self._print_serial(content, config)
                elif config.connection_type == PrinterConnection.NETWORK:
                    success = await self._print_network(content, config)
                elif config.connection_type == PrinterConnection.FILE:
                    success = await self._print_file(content, config)
                else:
                    logger.error(f"❌ Unsupported connection type: {config.connection_type}")
                    return False
                
                if not success:
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error printing copy {copy + 1}: {e}")
                return False
        
        return True
    
    async def _print_windows_driver(self, content: str, config: PrinterConfig) -> bool:
        """Imprime usando driver Windows"""
        if not WIN32_AVAILABLE:
            logger.warning("⚠️ Windows printing not available, using file fallback")
            return await self._print_file(content, config)
        
        try:
            # Obtém impressora padrão ou especificada
            printer_name = config.name
            
            # Cria job de impressão
            hprinter = win32print.OpenPrinter(printer_name)
            
            try:
                job_info = ("Comprovante", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, content.encode(config.encoding))
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Windows printing error: {e}")
            return False
    
    async def _print_serial(self, content: str, config: PrinterConfig) -> bool:
        """Imprime via porta serial"""
        if not SERIAL_AVAILABLE:
            logger.warning("⚠️ Serial printing not available, using file fallback")
            return await self._print_file(content, config)
        
        try:
            with serial.Serial(
                port=config.port,
                baudrate=config.baudrate,
                timeout=config.connection_timeout
            ) as ser:
                ser.write(content.encode(config.encoding))
                ser.flush()
                
                # Aguarda impressão
                await asyncio.sleep(2)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Serial printing error: {e}")
            return False
    
    async def _print_network(self, content: str, config: PrinterConfig) -> bool:
        """Imprime via rede TCP/IP"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(config.connection_timeout)
                sock.connect((config.ip_address, config.tcp_port))
                sock.send(content.encode(config.encoding))
                
                # Aguarda impressão
                await asyncio.sleep(2)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Network printing error: {e}")
            return False
    
    async def _print_file(self, content: str, config: PrinterConfig) -> bool:
        """Salva em arquivo (impressora virtual)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{timestamp}.txt"
            
            # Cria diretório se não existir
            receipts_dir = Path("receipts")
            receipts_dir.mkdir(exist_ok=True)
            
            filepath = receipts_dir / filename
            
            with open(filepath, 'w', encoding=config.encoding) as f:
                f.write(content)
            
            logger.info(f"📄 Receipt saved to file: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ File printing error: {e}")
            return False
    
    # === Métodos Utilitários ===
    
    def _center_text(self, text: str, width: int) -> str:
        """Centraliza texto"""
        if len(text) >= width:
            return text[:width]
        
        padding = (width - len(text)) // 2
        return " " * padding + text
    
    def _format_cnpj(self, cnpj: str) -> str:
        """Formata CNPJ"""
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
    
    def _format_cpf(self, cpf: str) -> str:
        """Formata CPF"""
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    def _format_payment_method(self, method: str) -> str:
        """Formata método de pagamento"""
        methods = {
            "credit_card": "Cartao de Credito",
            "debit_card": "Cartao de Debito",
            "pix": "PIX",
            "boleto": "Boleto Bancario",
            "voucher": "Vale Refeicao/Alimentacao",
            "contactless": "Aproximacao"
        }
        return methods.get(method, method.title())
    
    def _format_status(self, status: str) -> str:
        status_map = {
            "paid": "Aprovado",
            "pending": "Pendente",
            "failed": "Recusado",
            "cancelled": "Cancelado"
        }
        return status_map.get(status.lower(), status.capitalize())

# Singleton instance of the printer service
printer_manager = PrinterService()
# 🔌 Protocolos de Comunicação para Terminais

import asyncio
import serial
import socket
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConnectionConfig:
    """Configuração de conexão"""
    connection_type: str
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class CommunicationProtocol(ABC):
    """Interface base para protocolos de comunicação"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connection = None
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Estabelece conexão"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Encerra conexão"""
        pass
    
    @abstractmethod
    async def send_command(self, command: bytes) -> bytes:
        """Envia comando e aguarda resposta"""
        pass
    
    @abstractmethod
    async def send_raw(self, data: bytes) -> bool:
        """Envia dados sem aguardar resposta"""
        pass

class SerialProtocol(CommunicationProtocol):
    """Protocolo de comunicação serial (USB/RS232)"""
    
    def __init__(self, config: ConnectionConfig, port: str, baudrate: int = 9600, 
                 bytesize: int = 8, parity: str = 'N', stopbits: int = 1):
        super().__init__(config)
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.serial_connection: Optional[serial.Serial] = None
    
    async def connect(self) -> bool:
        """Conecta via porta serial"""
        try:
            logger.info(f"🔌 Connecting to serial port {self.port} at {self.baudrate} baud")
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.config.timeout
            )
            
            if self.serial_connection.is_open:
                self.is_connected = True
                logger.info(f"✅ Serial connection established: {self.port}")
                return True
            else:
                logger.error(f"❌ Failed to open serial port: {self.port}")
                return False
                
        except serial.SerialException as e:
            logger.error(f"❌ Serial connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to serial: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta da porta serial"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                logger.info(f"🔌 Serial connection closed: {self.port}")
            
            self.is_connected = False
            self.serial_connection = None
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting serial: {e}")
            return False
    
    async def send_command(self, command: bytes) -> bytes:
        """Envia comando serial e aguarda resposta"""
        if not self.is_connected or not self.serial_connection:
            raise ConnectionError("Serial not connected")
        
        try:
            # Limpa buffer de entrada
            self.serial_connection.reset_input_buffer()
            
            # Envia comando
            self.serial_connection.write(command)
            self.serial_connection.flush()
            
            logger.debug(f"📤 Sent serial command: {command.hex()}")
            
            # Aguarda resposta
            response = b""
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < self.config.timeout:
                if self.serial_connection.in_waiting > 0:
                    chunk = self.serial_connection.read(self.serial_connection.in_waiting)
                    response += chunk
                    
                    # Verifica se resposta está completa (implementar lógica específica)
                    if self._is_response_complete(response):
                        break
                
                await asyncio.sleep(0.01)  # Pequena pausa para não sobrecarregar CPU
            
            logger.debug(f"📥 Received serial response: {response.hex()}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Serial command error: {e}")
            raise
    
    async def send_raw(self, data: bytes) -> bool:
        """Envia dados sem aguardar resposta"""
        if not self.is_connected or not self.serial_connection:
            return False
        
        try:
            self.serial_connection.write(data)
            self.serial_connection.flush()
            return True
        except Exception as e:
            logger.error(f"❌ Serial send error: {e}")
            return False
    
    def _is_response_complete(self, response: bytes) -> bool:
        """Verifica se a resposta está completa (implementar conforme protocolo)"""
        # Implementação básica - pode ser sobrescrita
        return len(response) > 0 and (response.endswith(b'\r\n') or response.endswith(b'\x03'))

class TCPProtocol(CommunicationProtocol):
    """Protocolo de comunicação TCP/IP"""
    
    def __init__(self, config: ConnectionConfig, host: str, port: int):
        super().__init__(config)
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
    
    async def connect(self) -> bool:
        """Conecta via TCP"""
        try:
            logger.info(f"🔌 Connecting to TCP {self.host}:{self.port}")
            
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.config.timeout
            )
            
            self.is_connected = True
            logger.info(f"✅ TCP connection established: {self.host}:{self.port}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"❌ TCP connection timeout: {self.host}:{self.port}")
            return False
        except Exception as e:
            logger.error(f"❌ TCP connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta TCP"""
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
                logger.info(f"🔌 TCP connection closed: {self.host}:{self.port}")
            
            self.is_connected = False
            self.reader = None
            self.writer = None
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting TCP: {e}")
            return False
    
    async def send_command(self, command: bytes) -> bytes:
        """Envia comando TCP e aguarda resposta"""
        if not self.is_connected or not self.writer or not self.reader:
            raise ConnectionError("TCP not connected")
        
        try:
            # Envia comando
            self.writer.write(command)
            await self.writer.drain()
            
            logger.debug(f"📤 Sent TCP command: {command.hex()}")
            
            # Aguarda resposta
            response = await asyncio.wait_for(
                self.reader.read(4096),  # Ajustar conforme necessário
                timeout=self.config.timeout
            )
            
            logger.debug(f"📥 Received TCP response: {response.hex()}")
            return response
            
        except asyncio.TimeoutError:
            logger.error("❌ TCP command timeout")
            raise
        except Exception as e:
            logger.error(f"❌ TCP command error: {e}")
            raise
    
    async def send_raw(self, data: bytes) -> bool:
        """Envia dados TCP sem aguardar resposta"""
        if not self.is_connected or not self.writer:
            return False
        
        try:
            self.writer.write(data)
            await self.writer.drain()
            return True
        except Exception as e:
            logger.error(f"❌ TCP send error: {e}")
            return False

class BluetoothProtocol(CommunicationProtocol):
    """Protocolo de comunicação Bluetooth"""
    
    def __init__(self, config: ConnectionConfig, device_address: str, port: int = 1):
        super().__init__(config)
        self.device_address = device_address
        self.port = port
        self.socket: Optional[socket.socket] = None
    
    async def connect(self) -> bool:
        """Conecta via Bluetooth"""
        try:
            logger.info(f"🔌 Connecting to Bluetooth device {self.device_address}")
            
            # Importar bluetooth apenas quando necessário
            try:
                import bluetooth
            except ImportError:
                logger.error("❌ PyBluez not installed. Install with: pip install pybluez")
                return False
            
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.settimeout(self.config.timeout)
            
            # Conecta ao dispositivo
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.socket.connect, 
                (self.device_address, self.port)
            )
            
            self.is_connected = True
            logger.info(f"✅ Bluetooth connection established: {self.device_address}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bluetooth connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta Bluetooth"""
        try:
            if self.socket:
                self.socket.close()
                logger.info(f"🔌 Bluetooth connection closed: {self.device_address}")
            
            self.is_connected = False
            self.socket = None
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting Bluetooth: {e}")
            return False
    
    async def send_command(self, command: bytes) -> bytes:
        """Envia comando Bluetooth e aguarda resposta"""
        if not self.is_connected or not self.socket:
            raise ConnectionError("Bluetooth not connected")
        
        try:
            # Envia comando
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.socket.send, 
                command
            )
            
            logger.debug(f"📤 Sent Bluetooth command: {command.hex()}")
            
            # Aguarda resposta
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.socket.recv, 
                4096
            )
            
            logger.debug(f"📥 Received Bluetooth response: {response.hex()}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Bluetooth command error: {e}")
            raise
    
    async def send_raw(self, data: bytes) -> bool:
        """Envia dados Bluetooth sem aguardar resposta"""
        if not self.is_connected or not self.socket:
            return False
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.socket.send, 
                data
            )
            return True
        except Exception as e:
            logger.error(f"❌ Bluetooth send error: {e}")
            return False

class USBProtocol(CommunicationProtocol):
    """Protocolo de comunicação USB (usando pyusb)"""
    
    def __init__(self, config: ConnectionConfig, vendor_id: int, product_id: int, 
                 interface: int = 0, endpoint_out: int = 0x02, endpoint_in: int = 0x81):
        super().__init__(config)
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.interface = interface
        self.endpoint_out = endpoint_out
        self.endpoint_in = endpoint_in
        self.device = None
    
    async def connect(self) -> bool:
        """Conecta via USB"""
        try:
            logger.info(f"🔌 Connecting to USB device {self.vendor_id:04x}:{self.product_id:04x}")
            
            # Importar usb apenas quando necessário
            try:
                import usb.core
                import usb.util
            except ImportError:
                logger.error("❌ PyUSB not installed. Install with: pip install pyusb")
                return False
            
            # Encontra o dispositivo
            self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
            
            if self.device is None:
                logger.error(f"❌ USB device not found: {self.vendor_id:04x}:{self.product_id:04x}")
                return False
            
            # Configura o dispositivo
            if self.device.is_kernel_driver_active(self.interface):
                self.device.detach_kernel_driver(self.interface)
            
            self.device.set_configuration()
            usb.util.claim_interface(self.device, self.interface)
            
            self.is_connected = True
            logger.info(f"✅ USB connection established: {self.vendor_id:04x}:{self.product_id:04x}")
            return True
            
        except Exception as e:
            logger.error(f"❌ USB connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta USB"""
        try:
            if self.device:
                import usb.util
                usb.util.release_interface(self.device, self.interface)
                logger.info(f"🔌 USB connection closed: {self.vendor_id:04x}:{self.product_id:04x}")
            
            self.is_connected = False
            self.device = None
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting USB: {e}")
            return False
    
    async def send_command(self, command: bytes) -> bytes:
        """Envia comando USB e aguarda resposta"""
        if not self.is_connected or not self.device:
            raise ConnectionError("USB not connected")
        
        try:
            # Envia comando
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.write,
                self.endpoint_out,
                command,
                self.config.timeout * 1000  # pyusb usa milissegundos
            )
            
            logger.debug(f"📤 Sent USB command: {command.hex()}")
            
            # Aguarda resposta
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.read,
                self.endpoint_in,
                4096,
                self.config.timeout * 1000
            )
            
            # Converte array para bytes
            response_bytes = bytes(response)
            
            logger.debug(f"📥 Received USB response: {response_bytes.hex()}")
            return response_bytes
            
        except Exception as e:
            logger.error(f"❌ USB command error: {e}")
            raise
    
    async def send_raw(self, data: bytes) -> bool:
        """Envia dados USB sem aguardar resposta"""
        if not self.is_connected or not self.device:
            return False
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.device.write,
                self.endpoint_out,
                data,
                self.config.timeout * 1000
            )
            return True
        except Exception as e:
            logger.error(f"❌ USB send error: {e}")
            return False 
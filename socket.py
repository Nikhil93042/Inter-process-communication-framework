"""
Socket-based IPC implementation
"""
import socket
import struct
from typing import Any, Optional
from .base import BaseIPC

class SocketIPC(BaseIPC):
    """Socket-based IPC implementation"""
    
    def __init__(self, name: str, host: str = 'localhost', port: int = 5000):
        super().__init__(name)
        self.host = host
        self.port = port
        self._socket = None
        self._is_server = False
    
    def connect(self, is_server: bool = False) -> bool:
        """Establish socket connection"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if is_server:
                self._socket.bind((self.host, self.port))
                self._socket.listen(1)
                self._socket, _ = self._socket.accept()
            else:
                self._socket.connect((self.host, self.port))
            self._is_server = is_server
            self._is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to socket: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close socket connection"""
        try:
            if self._socket:
                self._socket.close()
            self._is_connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting from socket: {e}")
            return False
    
    def send(self, data: Any) -> bool:
        """Send data through socket"""
        if not self._is_connected:
            return False
        try:
            serialized_data = self._serialize(data)
            # Send data length first
            self._socket.send(struct.pack('!I', len(serialized_data)))
            # Send the actual data
            self._socket.send(serialized_data)
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def receive(self) -> Optional[Any]:
        """Receive data from socket"""
        if not self._is_connected:
            return None
        try:
            # Receive data length first
            length_bytes = self._socket.recv(4)
            if not length_bytes:
                return None
            length = struct.unpack('!I', length_bytes)[0]
            
            # Receive the actual data
            data = b''
            while len(data) < length:
                chunk = self._socket.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            
            return self._deserialize(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None 
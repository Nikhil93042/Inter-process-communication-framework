"""
Pipe-based IPC implementation
"""
import os
from typing import Any, Optional
from .base import BaseIPC

class PipeIPC(BaseIPC):
    """Pipe-based IPC implementation"""
    
    def __init__(self, name: str, read_pipe: str, write_pipe: str):
        super().__init__(name)
        self.read_pipe = read_pipe
        self.write_pipe = write_pipe
        self._read_fd = None
        self._write_fd = None
    
    def connect(self) -> bool:
        """Establish pipe connection"""
        try:
            # Create pipes if they don't exist
            if not os.path.exists(self.read_pipe):
                os.mkfifo(self.read_pipe)
            if not os.path.exists(self.write_pipe):
                os.mkfifo(self.write_pipe)
            
            # Open pipes
            self._read_fd = open(self.read_pipe, 'rb')
            self._write_fd = open(self.write_pipe, 'wb')
            self._is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to pipes: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close pipe connection"""
        try:
            if self._read_fd:
                self._read_fd.close()
            if self._write_fd:
                self._write_fd.close()
            self._is_connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting from pipes: {e}")
            return False
    
    def send(self, data: Any) -> bool:
        """Send data through pipe"""
        if not self._is_connected:
            return False
        try:
            serialized_data = self._serialize(data)
            # Send data length first
            self._write_fd.write(len(serialized_data).to_bytes(4, 'big'))
            self._write_fd.write(serialized_data)
            self._write_fd.flush()
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def receive(self) -> Optional[Any]:
        """Receive data from pipe"""
        if not self._is_connected:
            return None
        try:
            # Read data length first
            length_bytes = self._read_fd.read(4)
            if not length_bytes:
                return None
            length = int.from_bytes(length_bytes, 'big')
            
            # Read the actual data
            data = self._read_fd.read(length)
            if not data:
                return None
            
            return self._deserialize(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None 
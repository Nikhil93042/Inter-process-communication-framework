"""
Shared Memory-based IPC implementation
"""
import mmap
import os
from typing import Any, Optional
from .base import BaseIPC

class SharedMemoryIPC(BaseIPC):
    """Shared Memory-based IPC implementation"""
    
    def __init__(self, name: str, size: int = 1024 * 1024):  # 1MB default
        super().__init__(name)
        self.size = size
        self._shm_name = f"/{name}_shm"
        self._shm_fd = None
        self._mmap = None
    
    def connect(self) -> bool:
        """Establish shared memory connection"""
        try:
            # Create shared memory file
            self._shm_fd = os.open(self._shm_name, os.O_CREAT | os.O_RDWR)
            os.ftruncate(self._shm_fd, self.size)
            
            # Map shared memory
            self._mmap = mmap.mmap(self._shm_fd, self.size, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)
            self._is_connected = True
            return True
        except Exception as e:
            print(f"Error connecting to shared memory: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close shared memory connection"""
        try:
            if self._mmap:
                self._mmap.close()
            if self._shm_fd:
                os.close(self._shm_fd)
            self._is_connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting from shared memory: {e}")
            return False
    
    def send(self, data: Any) -> bool:
        """Send data through shared memory"""
        if not self._is_connected:
            return False
        try:
            serialized_data = self._serialize(data)
            if len(serialized_data) > self.size - 4:  # 4 bytes for length
                raise ValueError("Data too large for shared memory")
            
            # Write data length and data
            self._mmap.seek(0)
            self._mmap.write(len(serialized_data).to_bytes(4, 'big'))
            self._mmap.write(serialized_data)
            self._mmap.flush()
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def receive(self) -> Optional[Any]:
        """Receive data from shared memory"""
        if not self._is_connected:
            return None
        try:
            self._mmap.seek(0)
            length_bytes = self._mmap.read(4)
            if not length_bytes:
                return None
            length = int.from_bytes(length_bytes, 'big')
            
            if length > self.size - 4:
                raise ValueError("Received data length too large")
            
            data = self._mmap.read(length)
            if not data:
                return None
            
            return self._deserialize(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None 
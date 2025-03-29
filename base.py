"""
Base class for all IPC mechanisms
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
import json
import msgpack

class BaseIPC(ABC):
    """Base class for all IPC mechanisms"""
    
    def __init__(self, name: str):
        self.name = name
        self._is_connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection"""
        pass
    
    @abstractmethod
    def send(self, data: Any) -> bool:
        """Send data"""
        pass
    
    @abstractmethod
    def receive(self) -> Optional[Any]:
        """Receive data"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is established"""
        return self._is_connected
    
    def _serialize(self, data: Any, use_msgpack: bool = True) -> bytes:
        """Serialize data to bytes"""
        if use_msgpack:
            return msgpack.packb(data)
        return json.dumps(data).encode()
    
    def _deserialize(self, data: bytes, use_msgpack: bool = True) -> Any:
        """Deserialize bytes to data"""
        if use_msgpack:
            return msgpack.unpackb(data)
        return json.loads(data.decode()) 
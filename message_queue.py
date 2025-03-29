"""
Message Queue-based IPC implementation
"""
import os
import sys
from typing import Any, Optional
from .base import BaseIPC

class MessageQueueIPC(BaseIPC):
    """Message Queue-based IPC implementation"""
    
    def __init__(self, name: str, key: int = 1234):
        super().__init__(name)
        self.key = key
        self._msgid = None
    
    def connect(self) -> bool:
        """Establish message queue connection"""
        try:
            import ipc
            self._msgid = ipc.msgget(self.key, ipc.IPC_CREAT | 0o666)
            self._is_connected = True
            return True
        except ImportError:
            print("Message Queue IPC is not supported on this platform")
            return False
        except Exception as e:
            print(f"Error connecting to message queue: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close message queue connection"""
        try:
            if self._msgid is not None:
                import ipc
                ipc.msgctl(self._msgid, ipc.IPC_RMID, 0)
            self._is_connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting from message queue: {e}")
            return False
    
    def send(self, data: Any) -> bool:
        """Send data through message queue"""
        if not self._is_connected:
            return False
        try:
            import ipc
            serialized_data = self._serialize(data)
            msg = ipc.msgbuf()
            msg.mtype = 1
            msg.mtext = serialized_data
            ipc.msgsnd(self._msgid, msg, 0)
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def receive(self) -> Optional[Any]:
        """Receive data from message queue"""
        if not self._is_connected:
            return None
        try:
            import ipc
            msg = ipc.msgbuf()
            ipc.msgrcv(self._msgid, msg, 0, 1, 0)
            return self._deserialize(msg.mtext)
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None 
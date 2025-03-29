"""
Comprehensive Inter-Process Communication Framework
Supports multiple IPC mechanisms including pipes, shared memory, message queues, and sockets.
"""

from .base import BaseIPC
from .pipe import PipeIPC
from .shared_memory import SharedMemoryIPC
from .socket import SocketIPC
from .zmq import ZMQIPC

__version__ = '1.0.0'
__all__ = [
    'BaseIPC',
    'PipeIPC',
    'SharedMemoryIPC',
    'SocketIPC',
    'ZMQIPC'
] 
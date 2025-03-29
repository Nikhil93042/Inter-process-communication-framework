"""
ZeroMQ-based IPC implementation
"""
import zmq
from typing import Any, Optional
from .base import BaseIPC

class ZMQIPC(BaseIPC):
    """ZeroMQ-based IPC implementation"""
    
    def __init__(self, name: str, address: str = "tcp://localhost:5555"):
        super().__init__(name)
        self.address = address
        self._context = None
        self._socket = None
        self._is_server = False
        print(f"Initialized ZMQIPC with name={name}, address={address}")
    
    def connect(self, is_server: bool = False) -> bool:
        """Establish ZMQ connection"""
        try:
            print(f"Creating ZMQ context...")
            self._context = zmq.Context()
            
            socket_type = zmq.REP if is_server else zmq.REQ
            print(f"Creating {'server' if is_server else 'client'} socket...")
            self._socket = self._context.socket(socket_type)
            
            if is_server:
                print(f"Binding server to {self.address}...")
                self._socket.bind(self.address)
            else:
                print(f"Connecting client to {self.address}...")
                self._socket.connect(self.address)
            
            self._is_server = is_server
            self._is_connected = True
            print("ZMQ connection established successfully")
            return True
        except Exception as e:
            print(f"Error connecting to ZMQ: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close ZMQ connection"""
        try:
            if self._socket:
                print("Closing ZMQ socket...")
                self._socket.close()
            if self._context:
                print("Terminating ZMQ context...")
                self._context.term()
            self._is_connected = False
            print("ZMQ disconnected successfully")
            return True
        except Exception as e:
            print(f"Error disconnecting from ZMQ: {e}")
            return False
    
    def send(self, data: Any) -> bool:
        """Send data through ZMQ"""
        if not self._is_connected:
            print("Cannot send: not connected")
            return False
        try:
            print("Serializing data...")
            serialized_data = self._serialize(data)
            print(f"Sending {len(serialized_data)} bytes...")
            self._socket.send(serialized_data)
            print("Data sent successfully")
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
    
    def receive(self) -> Optional[Any]:
        """Receive data from ZMQ"""
        if not self._is_connected:
            print("Cannot receive: not connected")
            return None
        try:
            print("Waiting to receive data...")
            data = self._socket.recv()
            print(f"Received {len(data)} bytes")
            result = self._deserialize(data)
            print("Data deserialized successfully")
            return result
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None 
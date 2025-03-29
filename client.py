from ipc_framework import ZMQIPC
import time

def main():
    print("Creating ZMQ client...")
    # Create ZMQ client
    client = ZMQIPC("test_client", address="tcp://localhost:5556")
    
    print("Connecting client...")
    # Connect as client
    if not client.connect():
        print("Failed to connect client")
        return
    
    print("Client connected, sending messages...")
    
    try:
        # Send a test message
        message = {
            "type": "test",
            "content": "Hello from client!",
            "timestamp": time.time()
        }
        
        print("Sending message...")
        if client.send(message):
            print("Client sent message")
            
            # Wait for response
            print("Waiting for response...")
            response = client.receive()
            if response:
                print(f"Client received response: {response}")
            else:
                print("No response received")
        else:
            print("Failed to send message")
    
    except KeyboardInterrupt:
        print("\nClient shutting down...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 
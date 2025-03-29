from ipc_framework import ZMQIPC
import time

def main():
    print("Creating ZMQ server...")
    # Create ZMQ server
    server = ZMQIPC("test_server", address="tcp://*:5556")  # Changed port to 5556
    
    print("Connecting server...")
    # Connect as server
    if not server.connect(is_server=True):
        print("Failed to connect server")
        return
    
    print("Server started, waiting for messages...")
    
    try:
        while True:
            # Receive message
            print("Waiting for message...")
            data = server.receive()
            if data:
                print(f"Server received: {data}")
                
                # Send response
                response = {"status": "received", "data": data}
                print("Sending response...")
                if server.send(response):
                    print("Server sent response")
                else:
                    print("Failed to send response")
            
            time.sleep(0.1)  # Small delay to prevent CPU overuse
    
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server.disconnect()

if __name__ == "__main__":
    main() 
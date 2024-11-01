import socket
import sys
import os


def start_client(host, port, action, filename=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10)

    try:
        client_socket.connect((host, port))

        if action == "put" and filename:
            if not os.path.exists(filename):
                print (f"Error: '{filename}' does not exist.")
                return
            
            client_socket.send(f"put {filename}".encode('utf-8'))
            with open(filename, 'rb') as f:
                while chunk := f.read(1024):
                    client_socket.send(chunk)
            
            
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Response from the server: {response}")
        
        elif action == "get" and filename:
            if os.path.exists(filename):
                print(f"Error: '{filename}' already")
            client_socket.send(f"get {filename}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            if response == "Error: File does not exist":
                print("Error: File was not found on the server.")
                return
            
            with open(filename, 'wb') as f:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)

            print(f"'{filename}' downloaded.")
        
        elif action == "list":
            client_socket.send("list".encode('utf-8'))
            directory_listing = client_socket.recv(4096).decode('utf-8')
            print("Directory List:\n" + directory_listing)
        
        else:
            print("Unknown action or missing filename")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) <3:
        print("Usage: python client.py <host> <port> <action> <filename>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    action = sys.argv[3]
    filename = sys.argv[4] if len(sys.argv) > 4 else None

    start_client(host, port, action, filename)

import socket
import sys
import os


def start_server (port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"Server is running on port: {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_client(client_socket, client_address)


def handle_client (client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode("UTF-8")
        parts = request.split()

        if len(parts) <1:
            client_socket.send("Incorrect request format".encode('utf-8'))
            print(f"Incorrect request from {client_address}")
            return

        action = parts[0]
        filename = parts [1] if len(parts)> 1 else None

        if action == "put":
            receive_file(client_socket ,filename)
        elif action == "get":
            send_file(client_socket, filename)
        elif action == "list":
            send_directory_listing(client_socket)
        else:
            client_socket.send("Error: Unknown action".encode('utf-8'))
            print(f"Unknown request '{action}' from {client_address}")
    except Exception as e:
        print (f"Error handling request from {client_address}: {str(e)}")
    finally:
        client_socket.close()


def receive_file(client_socket, filename):
    try:
        if os.path.exists(filename):
            client_socket.send("Error: File already exists".encode('utf-8'))
            return
    
        with open(filename, 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)

        client_socket.send("File uploaded successfully".encode('utf-8'))
        print(f"'{filename}' received and saved.")
    except Exception as e:
        print(f"Error during file upload '{filename}': {str(e)}")
        if os.path.exists(filename):
            os.remove(filename) #removes incomplete file

def send_file(client_socket, filename):
    try:

        if not os.path.exists(filename):
            client_socket.send("Error: File does not exist".encode('utf-8'))
            return
        
        client_socket.send("OK".encode("UTF-8"))
        with open(filename, 'rb') as f:
            while chunk := f.read(1024):
                client_socket.send(chunk)
        client_socket.send(b"") #send an incomplete byte to indicate the end of the transfer
        print(f"'{filename}' sent to the client.")
    
    except Exception as e:
        print(f"Error during file download of '{filename}': {str(e)}")

def send_directory_listing(client_socket):
    try:
        files = os.listdir(".")
        files_list = "\n".join(files)
        client_socket.send(files_list.encode('utf-8'))
        print("Directory List sent to the client.")
    except Exception as e:
        client_socket.send(f"Error: {str(e)}".encode('utf-8'))
        print(f"Error during send the directory list: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    start_server(port)

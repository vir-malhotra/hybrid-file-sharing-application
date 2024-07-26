import socket
import os

data_dict = {}


def handle_connection(conn):
    with conn:
        # Receive the initial message
        data = conn.recv(1024).decode('utf-8')
        print(data)

        # Determine the type of message
        if data.startswith('NOTIFY'):
            # Handle notification
            print("Received notification:", data)
            chunk_id, chunk_size = data.split(':')[1:]
            print(f"Preparing to receive chunk {chunk_id} of size {chunk_size} bytes")

        elif data.startswith('CHUNK'):
            # Extract chunk ID and expect the chunk data
            chunk_id, chunk_size, file_path, chunk_data = data.split(',')[1:]
            chunk_size = int(chunk_size)
            print(f"Receiving chunk {chunk_id} of size {chunk_size} bytes")
            print(f"The data in chunk {chunk_id} is: {chunk_data}")

            chunk_id_filename = file_path.split('/')
            data_dict[chunk_id_filename[-1]] = chunk_data
            # Prepare to receive the chunk data

        if data.startswith('REQUEST'):
            # Extract the requested chunk ID
            _, chunk_id = data.split(' ')
            print(f"Peer requested chunk: {chunk_id}")

            # Send the requested chunk
            send_chunk(conn, chunk_id)

def send_chunk(conn, chunk_id):
    """Sends the specified chunk to the requester."""
    chunk_filename = f"received_chunk_{chunk_id}"
    if chunk_id in data_dict.keys():
        chunk_data = data_dict[chunk_id]

        # Convert chunk data to bytes (if it's not already in bytes)
        if isinstance(chunk_data, str):
            chunk_data = chunk_data.encode('utf-8')  # Encode string to bytes

        # Send the size of the chunk first, followed by a newline character as a delimiter
        size_info = str(len(chunk_data)).encode('utf-8') + b'\n'
        conn.sendall(size_info)

        # Send the actual chunk data
        conn.sendall(chunk_data)
        print(f"Sent chunk {chunk_id}: {size_info.strip()} bytes followed by data.")
    else:
        print(f"Chunk {chunk_id} not found.")



def start_receiver(host='localhost', port=8001):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            print('Connected by', addr)
            handle_connection(conn)


if __name__ == "__main__":
    # Example usage: Start the receiver on localhost port 8002
    start_receiver(host='localhost', port=8002)


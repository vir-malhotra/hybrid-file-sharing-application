import socket
import os

# Define the tracker host and port
tracker_host = 'localhost'
tracker_port = 9001

# Define the directory to download chunks to and the base filename for the reconstructed file
download_directory = 'C:/Users/Vir Malhotra/Desktop/Networkss Project - IP/downloaded_chunk'
file_name = 'reconstructed_file'  # Name of the final reconstructed file

# Create the directory if it does not exist
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

def query_tracker_for_peers(chunk_id):
    """Ask the tracker for a list of peers that have the specified chunk."""
    print("Querying tracker for peers...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((tracker_host, tracker_port))  # Connect to the tracker
        query_message = f'QUERY {chunk_id}'
        sock.sendall(query_message.encode('utf-8'))  # Send the query message
        response = sock.recv(1024).decode('utf-8')  # Receive the response from the tracker
    return response.split()  # Split the response into a list of peers

def download_chunk_from_peer(peer_info, chunk_id):
    """Download a chunk from the specified peer."""
    print("Attempting to connect to peer:", peer_info)
    peer_host, peer_port = peer_info.split(':')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((peer_host, int(peer_port)))  # Connect to the peer
        print(chunk_id)
        request_message = f'REQUEST {chunk_id}'
        sock.sendall(request_message.encode('utf-8'))  # Send a request for the chunk

        # Receive the size of the chunk, delimited by a newline
        size_data = b''
        while b'\n' not in size_data:
            size_data += sock.recv(1)
            if len(size_data) > 64:
                raise ValueError("Size data too long, something went wrong with the protocol")
        try:
            chunk_size_str = size_data.decode('utf-8').strip()
            chunk_size = int(chunk_size_str)
        except ValueError as e:
            print(f"Failed to convert received size to int: '{chunk_size_str}'")
            raise e

        if not chunk_size_str.isdigit():
            raise ValueError(f"Received chunk size is not a digit, received: '{chunk_size_str}'")

        # Receive the actual chunk data
        chunk_data = b''
        while len(chunk_data) < chunk_size:
            to_read = min(chunk_size - len(chunk_data), 4096)
            data = sock.recv(to_read)
            if not data:
                break
            chunk_data += data

        if len(chunk_data) < chunk_size:
            print(f"Error: Expected to receive {chunk_size} bytes, received only {len(chunk_data)} bytes.")
        else:
            print("Received chunk data successfully.")

    return chunk_data

def reconstruct_file(chunks, output_file_path):
    """Reconstruct the original file from its chunks."""
    with open(output_file_path, 'wb') as output_file:
        for chunk_data in chunks:
            output_file.write(chunk_data)  # Write each chunk's data into the file sequentially

def main():
    while True:
        print("\nMenu:")
        print("1. Download a file")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            chunk_id = input("Enter the chunk ID you want to download:")
            downloaded_chunks = []
            peers = query_tracker_for_peers(chunk_id)  # Get a list of peers that have the chunk
            if not peers:
                print(f"No peers found for chunk {chunk_id}")
                continue

            # Attempt to download the chunk from each peer listed
            for peer_info in peers:
                chunk_data = download_chunk_from_peer(peer_info, chunk_id)
                downloaded_chunks.append(chunk_data)

            print(f"Chunk {chunk_id} downloaded and saved.")

            # Reconstruct the original file from downloaded chunks
            output_file_path = os.path.join(download_directory, f"{file_name}_{chunk_id}")
            reconstruct_file(downloaded_chunks, output_file_path)
            print(f"File reconstructed as {output_file_path}")
        elif choice == '2':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()

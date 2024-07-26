import socket
import threading

class Tracker:
    def __init__(self, host='localhost', port=9001):
        # Initialize the Tracker with a host (default 'localhost') and port number (default 9001).
        self.host = host
        self.port = port
        self.peer_chunks = {}  # This dictionary will map chunk IDs to a list of peers (clients) that have this chunk.

    def print_details(self):
        # Print details of all the chunks and their associated peers.
        print("Tracker Details:")
        for chunk_id, peers in self.peer_chunks.items():
            print(f"Chunk ID: {chunk_id}, Peers: {peers}")

    def start(self):
        # Start the Tracker server to listen for connections.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))  # Bind the socket to the host and port.
            server_socket.listen()  # Listen for incoming connections.
            print(f"Tracker listening on {self.host}:{self.port}")
            while True:
                conn, _ = server_socket.accept()  # Accept a new connection.
                # Handle each connection in a new thread to allow multiple clients to connect.
                threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        # This method handles the connection from each peer.
        with conn:
            data = conn.recv(1024).decode('utf-8')  # Receive data from the peer, decode it from bytes to string.
            parts = data.strip().split(' ')  # Split the received data into parts.
            command = parts[0]  # The first part is the command: REGISTER or QUERY.

            if command == 'REGISTER':
                # If the command is REGISTER, register the peer for the specified chunk.
                chunk_id = " ".join(parts[1:-1])  # The chunk ID is all parts except the last (peer_id).
                peer_id = parts[-1]  # The last part is the peer_id.
                filename = chunk_id.split('/')
                self.register_peer(peer_id, filename[-1])  # Register the peer.
                self.print_details()  # Print the current details of all chunks.
                print(self.peer_chunks)  # Debug print of the peer_chunks dictionary.
            elif command == 'QUERY':
                # If the command is QUERY, send the list of peers that have the specified chunk.
                chunk_id = parts[1]  # The second part is the chunk ID.
                self.send_peer_list(conn, chunk_id)  # Send the list of peers to the requester.

    def register_peer(self, peer_id, chunk_id):
        # Register a peer for a specific chunk.
        if chunk_id not in self.peer_chunks:
            self.peer_chunks[chunk_id] = []  # If chunk_id is not in the dictionary, initialize it.
        self.peer_chunks[chunk_id].append(peer_id)  # Append the peer_id to the list of peers for this chunk.
        print(f"Registered {peer_id} for chunk {chunk_id}")  # Print a confirmation message.

    def send_peer_list(self, conn, chunk_id):
        # Send the list of peers that have a specific chunk to the requester.
        peers = ' '.join(self.peer_chunks.get(chunk_id, []))  # Get the list of peers as a space-separated string.
        conn.sendall(peers.encode('utf-8'))  # Send the peers list as bytes over the connection.

if __name__ == "__main__":
    Tracker().start()  # If this script is executed as the main program, start the Tracker.

'''Networks Project 1
Group Members: Vir Malhotra, Irfan Karukappadath, Mishka Parikh
The code in the submission is for running the program on one device, but the video demonstrates that it can be run using multiple devices as well.
Files have been included from an example run'''



import os
import socket

tracker_host = 'localhost'
tracker_port = 9001

# Step 1: Chunk the file
def split_file_into_two(file_path):

    # Determine the size of the file
    total_size = os.path.getsize(file_path)
    part_size = total_size // 2

    base_name, extension = os.path.splitext(file_path)

    # Generate filenames for the two parts while retaining the original extension
    part1_filename = f"{base_name}_part_1{extension}"
    part2_filename = f"{base_name}_part_2{extension}"

    #Open the original file to start reading
    with open(file_path, 'rb') as file:

        # Read and write the first part
        part1_data = file.read(part_size)
        with open(part1_filename, 'wb') as part1_file:
            part1_file.write(part1_data)

        # Read and write the second part
        part2_data = file.read()  # Read the rest of the file
        with open(part2_filename, 'wb') as part2_file:
            part2_file.write(part2_data)

    chunk_filenames = []
    chunk_filenames.append(part1_filename)
    chunk_filenames.append(part2_filename)

    return chunk_filenames


# Step 2: Notify peers and send chunks
def notify_and_send_chunks(peer_host, peer_port, chunk_filename, file_path):

    # Open the chunk file and read its contents
    with open(chunk_filename, 'rb') as file:
        chunk_data = file.read()

    # Extract the chunk ID from the filename
    chunk_id = os.path.basename(chunk_filename).split('_')[-1][0]
    chunk_size = len(chunk_data)

    # Notify the peer about the chunk and then send the chunk data
    notify_peer(peer_host, peer_port, chunk_id, chunk_size)
    send_chunk_to_peer(peer_host, peer_port, chunk_id, chunk_data, file_path)
    register_chunk_with_tracker(file_path, f"{peer_host}:{peer_port}")


def notify_peer(peer_host, peer_port, chunk_id, chunk_size):
    message = f"NOTIFY:{chunk_id}:{chunk_size}"
    send_message_to_peer(peer_host, peer_port, message)


# Revised to handle binary data correctly
def send_chunk_to_peer(peer_host, peer_port, chunk_id, chunk_data, file_path):
    message = f"CHUNK,{chunk_id},{len(chunk_data)},{file_path},"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
        peer_socket.connect((peer_host, peer_port))
        peer_socket.sendall(message.encode('utf-8'))
        peer_socket.sendall(chunk_data)


def send_message_to_peer(peer_host, peer_port, message, data=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
        peer_socket.connect((peer_host, peer_port))
        peer_socket.sendall(message.encode('utf-8'))
        if data:
            peer_socket.sendall(data)


def register_chunk_with_tracker(chunk_id, peer_info):
    message = f"REGISTER {chunk_id} {peer_info}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tracker_socket:
        tracker_socket.connect((tracker_host, tracker_port))
        tracker_socket.sendall(message.encode('utf-8'))


def main_menu():
    while True:
        print("\nMenu:")
        print("1. Send a file")
        print("2. Quit")
        choice = input("Enter your choice: ")
        file_path_def = "C:/Users/Vir Malhotra/Desktop/Networkss Project - IP/"
        if choice == '1':
            file_name = input("Enter the full path of the file to send: ")
            file_name = file_path_def + file_name
            if os.path.exists(file_name):
                chunk_filenames = split_file_into_two(file_name)
                peers = [("localhost", 8001), ("localhost", 8002)]  # peer addresses

                # Send each chunk to a corresponding peer
                for index, (peer_host, peer_port) in enumerate(peers):
                    print("Trying to send to", peer_host, peer_port)
                    notify_and_send_chunks(peer_host, peer_port, chunk_filenames[index], file_name)
            else:
                print("File does not exist. Please try again.")
        elif choice == '2':
            print("Quitting program.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


main_menu()

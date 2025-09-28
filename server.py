import sys
import os
import threading
from socket import *
import pickle

SERVER_IP = "172.17.0.3"
WELCOME_MESSAGE = f"Welcome to {SERVER_IP} file server"
WELCOME_BLOCKS = 1
BUFFER_SIZE = 512
MAX_PACKAGE_SIZE = 540
DIRECTORY_PATH = "."
DIR_COMMAND = ""
FILE_NOT_FOUND = "File not found"

RRQ = 1
DAT = 3
ACK = 4
ERR = 5

error = False
ended = False

dir_list = os.listdir(DIRECTORY_PATH)


def closeSocket(sock):
    sock.close()


def acknowledge(sock, block_count):
    package = sock.recv(MAX_PACKAGE_SIZE)
    opcode, block_number = pickle.loads(package)
    print("this is ack")
    if not (opcode == ACK and block_number == block_count):
        error = True
        print("ERRROR", block_count)


def send_dirs(sock):
    block_count = 1
    for path in os.listdir(DIRECTORY_PATH):
        # check if current path is a file
        if os.path.isfile(os.path.join(DIRECTORY_PATH, path)):
            package = (DAT, block_count, len(path), path)
            sock.send(pickle.dumps(package))
            acknowledge(sock, block_count)
            block_count += 1
    # Empty last block to signal transfer is over
    sock.send(pickle.dumps((DAT, block_count, 0, "")))


def send_file(filename, sock):
    try:
        file = open(filename, "rb")
        file_size = os.path.getsize(filename)
        total_blocks = (file_size/BUFFER_SIZE) + 1
        block_count = 1
        acknowledged = True
        while block_count <= total_blocks and acknowledged:
            if block_count == total_blocks:
                size = file_size - (BUFFER_SIZE * total_blocks)
            else:
                size = BUFFER_SIZE

            file_data = file.read(BUFFER_SIZE)
            requested_package = (DAT, block_count, size, file_data)
            sock.send(pickle.dumps(requested_package))
            rp = pickle.dumps(requested_package)
            pickle.loads(rp)
            print(len(rp))

            print(str(file_data))
            print(block_count)
            acknowledge(sock, block_count)

            if error:
                break
            block_count += 1
    except:
        sock.send(pickle.dumps((ERR, FILE_NOT_FOUND)))



def analyse_package(op_code, package, sock):
    if op_code == RRQ:
        filename = package[1]
        if filename == DIR_COMMAND:
            send_dirs(sock)
        else:
            print("File requested is ", filename)
            send_file(filename, sock)
    else:
        error = True


def handle_client(sock):
    # Welcome message
    welcome_package = (DAT, WELCOME_BLOCKS, len(WELCOME_MESSAGE), WELCOME_MESSAGE)
    sock.send(pickle.dumps(welcome_package))
    acknowledge(sock, WELCOME_BLOCKS)

    # Process packages
    while not (error or ended):
        buffer = sock.recv(MAX_PACKAGE_SIZE)
        if not buffer:
            print("Client Disconnected")
            break
        received_package = pickle.loads(buffer)
        op_code = received_package[0]
        analyse_package(op_code, received_package, sock)


def main():
    try:
        if len(sys.argv) != 2 :
            print("Error: Incorrect number of arguments.")
            sys.exit(1)

        server_port = sys.argv[1]

        serverSocket = socket(AF_INET,SOCK_STREAM)
        serverSocket.bind((SERVER_IP, int(server_port)))

        print(server_port)

        serverSocket.listen(5)

        print("Server is running")

        while True:
            connSocket, client_addr = serverSocket.accept()

            print("Connected to: ", str(client_addr))
            tid = threading.Thread(target=handle_client, args=(connSocket,))
            tid.start()

            #connSocket.close()
    except Exception as e:
        print(e)
        print("Unable to start server")


main()

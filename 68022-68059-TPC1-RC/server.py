import sys
import os
import threading
import socket
import pickle

# Constants
SERVER_IP = ""
WELCOME_BLOCKS = 1
BUFFER_SIZE = 512
MAX_PACKAGE_SIZE = 540
DIRECTORY_PATH = "."
DIR_COMMAND = ""

# Messages
WELCOME_MESSAGE = "Welcome to {} file server"
FILE_NOT_FOUND = "File not found"
CLIENT_DISCONECTED = "Client Disconnected"
ERR_NUM_ARGUMENTS = "Error: Incorrect number of arguments."
SERVER_RUNNING = "Server is running"
UNABLE_TO_START = "Unable to start server"
SHUTTING_DOWN = "\nShutting down server..."


# op_codes:
RRQ = 1
DAT = 3
ACK = 4
ERR = 5


error = False
dir_list = os.listdir(DIRECTORY_PATH)

# Sends welcome message
def welcome(sock, local_ip):
    welcome_message = WELCOME_MESSAGE.format(local_ip)
    welcome_package = (DAT, WELCOME_BLOCKS, len(welcome_message), welcome_message)
    sock.send(pickle.dumps(welcome_package))
    acknowledge(sock, WELCOME_BLOCKS)



# Checks if ACK package was received
def acknowledge(sock, block_count):
    global error
    package = sock.recv(MAX_PACKAGE_SIZE)
    opcode, block_number = pickle.loads(package)
    if not (opcode == ACK and block_number == block_count):
        error = True


# Sends directory's files packages
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


# Sends a file to the client
def send_file(filename, sock):
    try:
        file = open(filename, "rb")
        file_size = os.path.getsize(filename)
        total_blocks = (file_size/BUFFER_SIZE) + 1
        block_count = 1
        acknowledged = True
        while block_count <= total_blocks and acknowledged:
            file_data = file.read(BUFFER_SIZE)
            size = len(file_data)
            requested_package = (DAT, block_count, size, file_data)
            sock.send(pickle.dumps(requested_package))
            rp = pickle.dumps(requested_package)
            pickle.loads(rp)
            acknowledge(sock, block_count)

            if error:
                break
            block_count += 1
    except:
        sock.send(pickle.dumps((ERR, FILE_NOT_FOUND)))



# Analises the type of the package received based on the op_code
def analyse_package(op_code, package, sock):
    if op_code == RRQ:
        filename = package[1]
        if filename == DIR_COMMAND:
            send_dirs(sock)
        else:
            send_file(filename, sock)


# Thread function to handle a client
def handle_client(sock, local_ip):
    # Welcome message
    welcome(sock, local_ip)

    # Process packages
    while not error:
        buffer = sock.recv(MAX_PACKAGE_SIZE)
        if not buffer:
            print(CLIENT_DISCONECTED)
            break
        received_package = pickle.loads(buffer)
        op_code = received_package[0]
        analyse_package(op_code, received_package, sock)

    sock.close()


def main():
    try:
        if len(sys.argv) != 2 :
            print(ERR_NUM_ARGUMENTS)
            sys.exit(1)

        server_port = sys.argv[1]
        serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        serverSocket.bind((SERVER_IP, int(server_port)))
        local_ip = socket.gethostbyname(socket.gethostname())
        serverSocket.listen(5)
        print(SERVER_RUNNING)

        while True:
            connSocket, client_addr = serverSocket.accept()
            print("Connected to: ", str(client_addr))
            tid = threading.Thread(target=handle_client, args=(connSocket,local_ip))
            tid.start()

    except Exception as e:
        print(e)
        print(UNABLE_TO_START)
    except KeyboardInterrupt:
        print(SHUTTING_DOWN)



main()

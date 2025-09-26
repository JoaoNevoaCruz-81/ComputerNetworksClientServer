import sys
from socket import *
import threading

server_ip = "172.17.0.2"
welcome_message = f"Welcome to {server_ip} file server"
bufferSize = 512


def execute_command(cmd):
    match cmd:
        case "end":
            print("Goodbye!")
        case "dir":
            print("Dir command")
        case "get":
            print("Get command")


def handle_client(socket):
    socket.send(welcome_message.encode())

    while True:
        command = socket.recv(bufferSize).decode()
        execute_command(command)
        if command == "end":
            break


def main():

    if len(sys.argv) != 2 :
        print("Error: Incorrect number of arguments.")
        sys.exit(1)

    server_port = sys.argv[1]


    serverSocket = socket(AF_INET,SOCK_STREAM)

    serverSocket.bind(server_ip, server_port)

    serverSocket.listen(5)
    print("Server is running")

    while True:
        connSocket, client_addr = serverSocket.accept()

        print("Connected to: ", str(client_addr))
        tid = threading.Thread(target=handle_client, args=(connSocket))
        tid.start()

        connSocket.close()


main()

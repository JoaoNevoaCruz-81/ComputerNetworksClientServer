"""

"""
from socket import *
import sys
import pickle
import os


BUFFER_SIZE = 540
DATA_SIZE = 512
server_addr = sys.argv[1]
server_port = sys.argv[2]

#opcodes
RRQ = 1
DAT = 3
ACK = 4
ERR = 5


# Define the FileDoesNotExist exception
class FileDoesNotExist(Exception):
    pass

#Unpacks a packet from the server
def unpack_packet(block):
    return pickle.loads(block)

#Forms a packet of bytes
def form_packet(tuple):
    return pickle.dumps(tuple)

#Makes an acknowledge block with the given block number
def make_ack_block(block_number):
    return form_packet((ACK, block_number))

#Sends a request for the server's directory and
#prints the result
def dir(clientSocket):
    #send the request
    filename = ""
    clientSocket.send(form_packet((RRQ, filename)))
    (_, block_number, size, data) = unpack_packet(clientSocket.recv(BUFFER_SIZE))
    clientSocket.send(make_ack_block(block_number))
    #print the input
    while size != 0:
        print(data)
        (_, block_number, size, data) = unpack_packet(clientSocket.recv(BUFFER_SIZE))
        clientSocket.send(make_ack_block(block_number))


#Sends a request for a file and writes the content
def get(clientSocket, remote_fn, local_fn):
    #send request packet
    clientSocket.send(form_packet((RRQ, remote_fn)))
    expected_block_number = 1
    with open(local_fn, "wb") as f:
        while True:
            my_packet = unpack_packet(clientSocket.recv(BUFFER_SIZE))
            opcode = my_packet[0]
            match opcode:
                case 3:  # Data block
                    _, block_number, size, data = my_packet

                    # Check for protocol error
                    if block_number != expected_block_number:
                        close_connection(clientSocket)
                        os.remove(local_fn)
                        return
                    print(block_number)
                    print(size)
                    f.write(data)
                    clientSocket.send(make_ack_block(block_number))
                    expected_block_number += 1
                    if size < DATA_SIZE: # This was the last block
                        break

                case 5:  # Error packet
                    if(expected_block_number == 1): # File Does not Exist Exception
                        raise FileDoesNotExist
                    os.remove(local_fn)
                    print(my_packet[1]) # print error msg
                    close_connection(clientSocket)
                case _:  # Protocol error
                    f.close()
                    os.remove(local_fn)
                    close_connection(clientSocket)



#Closes the TCP connection
def close_connection(clientSocket):
    clientSocket.close()
    print("Connection close, client ended")
    sys.exit()




#Main function of the program
def main():

    #create a tcp connection
    clientSocket = socket(AF_INET,SOCK_STREAM)

    try:
        clientSocket.connect((server_addr, int(server_port)))
        print("Connect to server")
        #unpack the data block
        (opcode, block_number, size, data) = unpack_packet(clientSocket.recv(BUFFER_SIZE))
        print(data)
        #Send the ack block
        clientSocket.send(make_ack_block(block_number))
    except Exception as e:
        print(e)
        print("Unable to connect with the server")
        sys.exit()

    #Read input from the user
    cmd = input("client>").split()
    while cmd[0] != "end":
        match cmd[0]:
            case "dir":
                dir(clientSocket)
            case "get":
                if(len(cmd)< 3):
                    print("Invalid number of arguments")
                elif (cmd[2] in os.listdir(".")):
                    print("File exists in client")
                else:
                    try:
                        get(clientSocket, cmd[1], cmd[2])
                        print("File transfer completed")
                    except FileDoesNotExist:
                        print("File not found")
            case _:
                print("Unknown command")
        cmd = input("client>").split()

    close_connection(clientSocket)

main()

"""

"""
from socket import *
import sys
import pickle
import os


max_packet_size = 540
block_size = 512
server_addr = sys.argv[1]
server_port = sys.argv[2]


#opcodes
RRQ = 1
DAT = 3
ACK = 4
ERR = 5

# Define a custom exception
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

    filename = ""
    clientSocket.send(form_packet((RRQ, filename)))
    (_, block_number, size, data) = unpack_packet(clientSocket.recv(max_packet_size))

    clientSocket.send(make_ack_block(block_number))

    while size != 0:
        print(data)
        (_, block_number, size, data) = unpack_packet(clientSocket.recv(max_packet_size))
        clientSocket.send(make_ack_block(block_number))
    #print(data)

#Sends a request for a file and writes the content
def get(clientSocket, remote_fn, local_fn):
    #send request packet
    clientSocket.send(form_packet((RRQ, remote_fn)))
    f = open(local_fn,"wb")
    expected_block_number = 1

    #read the first packet
    my_packet = unpack_packet(clientSocket.recv(max_packet_size))
    opcode = my_packet[0]
    match opcode:
            case 3: #data block
                (_,block_number, size, data) = my_packet
                if(block_number != expected_block_number): #protocol error
                    close_connection()
                    os.remove(local_fn)
                else:
                    f.write(data)
                    clientSocket.send(make_ack_block(block_number))
                expected_block_number += 1
            case 5: # error packet
                os.remove(local_fn)
                print(my_packet[1])
                raise FileDoesNotExist
            case _: #protocol error
                f.close()
                os.remove(local_fn)
                close_connection(clientSocket)

    my_packet = unpack_packet(clientSocket.recv(max_packet_size))
    opcode = my_packet[0]
    while( size == 512):
        match opcode:
            case 3: #data block
                (_,block_number, size, data) = my_packet
                if(block_number != expected_block_number): #protocol error
                    close_connection()
                    os.remove(local_fn)
                else:
                    f.write(data)
                    clientSocket.send(make_ack_block(block_number))
                expected_block_number += 1
            case 5: # error packet
                os.remove(local_fn)
                print(my_packet[1])
            case _: #protocol error
                os.remove(local_fn)
                close_connection(clientSocket)
                f.close()
        my_packet = unpack_packet(clientSocket.recv(max_packet_size))
        opcode = my_packet[0]

    #read the last data packet
    match opcode:
            case 3: #data block
                (_,block_number, size, data) = my_packet
                if(block_number != expected_block_number): #protocol error
                    close_connection()
                    os.remove(local_fn)
                else:
                    f.write(data)
                    clientSocket.send(make_ack_block(block_number))
                expected_block_number += 1
            case 5: # error packet
                os.remove(local_fn)
                print(my_packet[1])
            case _: #protocol error
                os.remove(local_fn)
                close_connection(clientSocket)
                f.close()


    f.close()

#Closes the TCP connection
def close_connection(clientSocket):
    clientSocket.close()
    print("Connection close, client ended")




#Main function of the program
def main():

    #create a tcp connection
    clientSocket = socket(AF_INET,SOCK_STREAM)

    try:
        clientSocket.connect((server_addr, int(server_port)))
        print("Connect to server")
        #unpack the data block
        (opcode, block_number, size, data) = unpack_packet(clientSocket.recv(max_packet_size))
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

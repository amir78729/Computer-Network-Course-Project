import socket

local_IP = "127.0.0.1"
local_port = 53
bufferSize = 512

msgFromServer = "Hello UDP Client. Your code passed the test:)"

bytesToSend = str.encode(msgFromServer)

# Creating a UDP socket at server side
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket.bind((local_IP, local_port))

print("UDP server up and listening")

while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client: {}".format(message)
    clientIP = "Client IP Address: {}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)


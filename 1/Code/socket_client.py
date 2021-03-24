import socket

msgFromClient = "Hello Server:)"
bytesToSend = str.encode(msgFromClient)
server_IP = '80.80.80.80'
server_IP = '127.0.0.1'  # uncomment for testing
server_port = 53  # the port for DNS
bufferSize = 512

# Creating a UDP socket at client side
UDP_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
print('UDP socket has been created!')

# Send to server using created UDP socket
UDP_client_socket.sendto(bytesToSend, (server_IP, server_port))
print('The message has been sent to Server!\nPORT: {}\nADDRESS: {}'.format(server_port, server_IP))

msgFromServer = UDP_client_socket.recvfrom(bufferSize)

msg = "Message from Server {}".format(msgFromServer[0])
print(msg)

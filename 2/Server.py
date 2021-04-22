# first of all import the socket library 
import socket

class Server:
    def __init__(self):
        self.users = []

    def run_server(self):
        # next create a socket object
        s = socket.socket()
        print("Socket successfully created")

        # reserve a port on your computer in our
        # case it is 12345 but it can be anything
        port = 12345

        # Next bind to the port
        # we have not typed any ip in the ip field
        # instead we have inputted an empty string
        # this makes the server listen to requests
        # coming from other computers on the network
        s.bind(('', port))
        print("socket binded to %s" % (port))

        # put the socket into listening mode
        s.listen(5)
        print("socket is listening")

        # a forever loop until we interrupt it or
        # an error occurs
        while True:

            # Establish connection with client.
            print(self.users)
            c, addr = s.accept()
            print('Got connection from', addr)

            # send a thank you message to the client.
            # c.send(b'Thank you for connecting')
            recieved_message = c.recv(2048).decode('utf-8').split()
            if recieved_message[0] == 'login':
                if recieved_message[1] in self.users :
                    c.send('user is in the list'.upper().encode('utf-8'))
                else:
                    c.send('user does not exist'.upper().encode('utf-8'))



            # Close the connection with the client
        # c.close()


if __name__ == '__main__':
    server = Server()
    server.run_server()
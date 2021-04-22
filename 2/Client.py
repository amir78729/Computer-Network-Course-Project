# Import socket module
import socket
import getpass


if __name__ == '__main__':
    # Create a socket object
    s = socket.socket()
    # Define the port on which you want to connect
    port = 12345
    # connect to the server on local computer
    s.connect(('127.0.0.1', port))

    option = int(input(' 1 - login\n'
                       ' 2 - create new account\n'
                       '-1 - cancel\n'.upper()))
    if option == 1:
        print('login:'.upper())
        username = input(' > username:  '.upper())
        password = input(' > password:  '.upper())
        msg = 'login {} {}'.format(username, password)
        s.send(msg.encode('utf-8'))
    elif option == 2:
        print('new account:'.upper())
        username = input(' > username:  '.upper())
        password = input(' > password:  '.upper())
        msg = 'signup {} {}'.format(username, password)
        s.send(msg.encode('utf-8'))
    elif option == -1:
        print('canceled'.upper)

    # receive data from the server
    received_message = s.recv(2048).decode('utf-8')
    print(received_message)
    # close the connection
    s.close()
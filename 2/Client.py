# Import socket module
import socket
from database_functions import *
if __name__ == '__main__':
    # Create a socket object
    s = socket.socket()
    # Define the port on which you want to connect
    port = 12345
    # connect to the server on local computer

    flag = False  # a boolean variable to configure if the user can use the service or not
    s.connect(('127.0.0.1', port))

    option = int(input(' 1 - login\n'
                       ' 2 - create new account\n'
                       '-1 - cancel\n'.upper()))
    if option == -1:
        print('closing the connection...'.upper())
        s.close()
    else:
        # login
        if option == 1:
            print('login:'.upper())
            username = input(' > username:  '.upper())
            password = input(' > password:  '.upper())
            msg = 'login {} {}'.format(username, password)
            print(msg)
            s.send(msg.encode('utf-8'))
            # receive data from the server
            received_message = s.recv(2048).decode('utf-8')
            print(received_message)
            if received_message == 'logged in successfully'.upper():
                flag = True

        # creating a new account
        elif option == 2:
            print('new account:'.upper())
            username = input(' > username:  '.upper())
            password = input(' > password:  '.upper())
            msg = 'signup {} {}'.format(username, password)
            s.send(msg.encode('utf-8'))
            # receive data from the server
            received_message = s.recv(2048).decode('utf-8')
            print(received_message)
            if received_message == 'user created successfully'.upper():
                flag = True

        else:
            print('wrong input!'.upper())

    if not flag:
        print('connection closed\nplease try again later'.upper())
    else:
        print('welcome to the git service {}!'.format(username).upper())
        option = int(input('please select an option\n'
                           ' 1 - delete account'.upper()))

        if option == 1:
            if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                msg = 'delete-user {}'.format(username)
                s.send(msg.encode('utf-8'))
    # close the connection

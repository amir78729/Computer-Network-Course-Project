# Import socket module
import socket
import getpass

from database_functions import *

PORT = 12345
ADDRESS = socket.gethostbyname(socket.gethostname())
MESSAGE_SIZE_LENGTH = 64
ENCODING = 'utf-8'


def receive_message_from_server(c):
    message_length = int(c.recv(MESSAGE_SIZE_LENGTH).decode(ENCODING))
    received_message = c.recv(message_length).decode(ENCODING).upper()
    print(received_message)
    return received_message


def send_message(client, msg):
    message = msg.encode(ENCODING)

    message_length = len(message)
    message_length = str(message_length).encode(ENCODING)
    message_length += b' ' * (MESSAGE_SIZE_LENGTH - len(message_length))

    client.send(message_length)
    client.send(message)


def main():
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    flag = False  # a boolean variable to configure if the user can use the service or not
    s.connect((ADDRESS, PORT))

    option = int(input(' 1 - login\n'
                       ' 2 - create new account\n'
                       '-1 - cancel\n'.upper()))
    if option == -1:
        print('closing the connection...'.upper())
        # send_message(s, 'disconnect ')
        s.close()
    else:
        # login
        if option == 1:
            print('login:'.upper())
            username = input(' > username:  '.upper())
            password = input(' > password:  '.upper())
            msg = 'login {} {}'.format(username, password)
            # print(msg)
            send_message(s, msg)
            # s.send(msg.encode('utf-8'))
            # receive data from the server
            received_message = receive_message_from_server(s)
            # print(received_message)
            if received_message == 'logged in successfully'.upper():
                flag = True

        # creating a new account
        elif option == 2:
            print('new account:'.upper())
            username = input(' > username:  '.upper())
            password = input(' > password:  '.upper())

            msg = 'signup {} {}'.format(username, password)
            # s.send(msg.encode('utf-8'))

            send_message(s, msg)

            # receive data from the server
            received_message = receive_message_from_server(s)
            # print(received_message)
            if received_message == 'user created successfully'.upper():
                flag = True

        else:
            print('wrong input!'.upper())

    if not flag:
        print('connection closed\nplease try again later'.upper())
    else:
        while True:
            print('welcome to the git service {}!'.format(username).upper())
            option = int(input('please select an option\n'
                               ' 1 - create repository\n'
                               ' 2 - select repository\n'
                               ' 3 - show repositories\n'
                               ' 4 - delete user\n'
                               '-1 - disconnect from server\n'.upper()))

            if option == -1:
                if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                    msg = 'disconnect {}'.format(username)
                    send_message(s, msg)
                    break  # end of program

            elif option == 1:
                repository_name = input(' > repository name:  '.upper())
                msg = 'create-repo {} {}'.format(username, repository_name)
                send_message(s, msg)
                receive_message_from_server(s)

            elif option == 4:
                if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                    msg = 'delete-user {}'.format(username)
                    send_message(s, msg)
                    receive_message_from_server(s)
                    break  # end of program

    # close the connection


if __name__ == '__main__':
    main()
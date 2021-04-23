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
    connected_successfully = False
    while True:
        option = int(input(' 1 - login\n'
                           ' 2 - create new account\n'
                           '-1 - cancel\n'.upper()))
        if option == -1:
            print('closing the connection...'.upper())
            s.close()
            break
        else:
            if option == 1:
                print('login:'.upper())
                username = input(' > username:  '.upper())
                password = input(' > password:  '.upper())
                msg = 'login {} {}'.format(username, password)
                print(msg)
                s.send(msg.encode('utf-8'))
                print('xx')
                # receive data from the server
                received_message = s.recv(2048).decode('utf-8')
                print(received_message)
                if received_message == 'logged in successfully'.upper():
                    connected_successfully = True
                    break
                else:
                    continue
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
                    connected_successfully = True
                    break
                else:
                    continue
            else:
                print('wrong input! try again'.upper())
                continue

    if connected_successfully:
        print('connected successfully')
    else:
        print('connection closed'.upper())
    # close the connection

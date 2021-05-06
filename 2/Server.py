import socket
import datetime
from database_functions import *
from _thread import *
# import os
from directiry_management_functions import *
import threading


class Server:
    def __init__(self):

        self.PORT = 12345
        self.ADDRESS = socket.gethostbyname(socket.gethostname())
        self.MESSAGE_SIZE_LENGTH = 64
        self.ENCODING = 'utf-8'
        self.active_users = []
        self.ROOT_PATH = 'GIT'
        self.WORKING_DIRECTORY = os.getcwd()
        make_directory(self.ROOT_PATH, self.WORKING_DIRECTORY)
        self.WORKING_DIRECTORY = os.path.join(self.WORKING_DIRECTORY, self.ROOT_PATH)


        # connecting to the database
        git_user_password_database = "user_password.sql"
        self.conn_user_password = create_connection(git_user_password_database)
        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_passwords (
                                                    username text PRIMARY KEY,
                                                    password text
                                                ); """
        if self.conn_user_password is not None:
            create_table(self.conn_user_password, create_user_table_query)
        else:
            print("Error... Database is NOT active!")

        # connecting to the database
        git_user_info_database = "user_info.sql"
        self.conn_user_info = create_connection(git_user_info_database)
        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_info (
                                                        username text PRIMARY KEY,
                                                        password text
                                                    ); """
        if self.conn_user_info is not None:
            create_table(self.conn_user_info, create_user_table_query)
        else:
            print("Error... Database is NOT active!")

    def print_server_info(self):
        print('server info'.upper())
        print('\tnumber of users in database: {}'.format(len(get_table(self.conn_user_password, 'users_passwords'))).upper())
        print('\tnumber of active users: {}'.format(len(self.active_users)).upper())
        [print('\t\t- {}'.format(i)) for i in self.active_users]

    def add_user(self, username, password):
        insert_into_table(self.conn_user_password, 'users_passwords', 'username, password', (username, password))

    def send_message_to_client(self, c, msg):
        # c.send(message.upper().encode('utf-8'))
        message = msg.upper().encode(self.ENCODING)
        message_length = len(message)
        message_length = str(message_length).encode(self.ENCODING)
        message_length += b' ' * (self.MESSAGE_SIZE_LENGTH - len(message_length))
        c.send(message_length)
        c.send(message)

    def delete_user(self, username):
        delete_user_from_database(self.conn_user_password, username)

    # TODO: a single user cannot send message to server. I don'r know where the problem is
    #  Maybe using threads is the solution
    #  https://stackoverflow.com/questions/42222425/python-sockets-multiple-messages-on-same-connection

    def handle_client(self, c, addr):
        # c.send(str.encode('Server is working:'))
        print('someone is connected!'.upper())
        connected = True
        while connected:
            print('- ' * 20)
            self.print_server_info()
            print('waiting for clients...'.upper())
            # try:
            # print('waiting for clients...'.upper(), end='')
            # c, addr = s.accept()
            message_length = int(c.recv(self.MESSAGE_SIZE_LENGTH).decode(self.ENCODING))
            received_message = c.recv(message_length).decode(self.ENCODING).split()

            command = received_message[0]

            print('new connection!'
                  '\n\ttype    :\t{}'
                  '\n\tfrom    :\t{}:{}'
                  '\n\tat      :\t{}'.format(command, addr[0], addr[1],
                                             datetime.datetime.now().strftime("%c")).upper())

            if command == 'login':
                # if received_message[1] in self.users.keys():
                username, password = received_message[1], received_message[2]

                if check_if_user_exists(self.conn_user_password, username):
                    # if self.users[received_message[1]] == received_message[2]:
                    if check_password(self.conn_user_password, username, password):
                        self.send_message_to_client(c, 'logged in successfully')
                        print('\tstatus  :\tsuccessful'.upper())
                        self.active_users.append(username)
                    else:
                        self.send_message_to_client(c, 'wrong password!')
                        print('\tstatus  :\twrong password'.upper())
                else:
                    self.send_message_to_client(c, 'user does not exist')
                    print('\tstatus  :\tuser not found'.upper())

            elif command == 'signup':
                username, password = received_message[1], received_message[2]

                if check_if_user_exists(self.conn_user_password, username):
                    self.send_message_to_client(c, 'user already exists!')
                    print('\tstatus  :\tuser already exist!'.upper())
                else:
                    self.add_user(username, password)
                    self.send_message_to_client(c, 'user created successfully')
                    print('\tstatus  :\tsuccessful'.upper())
                    self.active_users.append(username)
                    make_directory(username, self.WORKING_DIRECTORY)

            elif command == 'delete-user':
                username = received_message[1]
                self.delete_user(username)
                self.send_message_to_client(c, 'user deleted successfully')
                print('\tstatus  :\tsuccessful'.upper())
                self.active_users.remove(username)
                remove_directory(username, self.WORKING_DIRECTORY)

            elif command == 'create-repo':
                username = received_message[1]
                repository_name = received_message[2]
                parent_directory = os.path.join(self.WORKING_DIRECTORY, username)
                make_directory(repository_name, parent_directory)
                print('\tstatus  :\tREPOSITORY \"{}\" CREATED FOR USER \"{}\"'.format(repository_name, username))
                self.send_message_to_client(c, 'repository created successfully')

            elif command == 'show-repo':
                username = received_message[1]
                repositories = os.listdir(os.path.join(self.WORKING_DIRECTORY, username))
                self.send_message_to_client(c, str(len(repositories)))
                for repo in repositories:
                    self.send_message_to_client(c, '\t- '+repo)


            # disconnecting
            elif command == 'disconnect':
                username = received_message[1]
                self.active_users.remove(username)
                connected = False

            else:
                print('bad input from client!'.upper())

            # except Exception as e:
            #     print('oops...something went wrong:'.upper())
            #     print(e)
            #     self.send_message_to_client(c, 'oops, something went wrong!')
        print('- ' * 20)
        self.print_server_info()
        print('waiting for clients...'.upper())
        c.close()

    def run_server(self):
        # delete_user_from_database(self.conn_user_password, 'amir')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ADDRESS, self.PORT))
        print('server is up...'.upper())
        s.listen()
        while True:
            c, addr = s.accept()
            th = threading.Thread(target=self.handle_client, args=(c, addr,))
            th.start()



if __name__ == '__main__':
    server = Server()
    server.run_server()

# first of all import the socket library 
import socket
import datetime
import csv
from database_functions import *


class Server:
    def __init__(self):
        # retrieve users to a dictionary from a csv file
        # with open('users.csv', mode='r') as infile:
        #     reader = csv.reader(infile)
        #     self.users = {rows[0]: rows[1] for rows in reader}

        git_database = "users.db"
        self.conn = create_connection(git_database)

        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_info (
                                                    username text PRIMARY KEY,
                                                    password text
                                                ); """

        if self.conn is not None:
            # create projects table
            create_table(self.conn, create_user_table_query)

        else:
            print("Error... Database is NOT active!.")

    def print_server_info(self):
        print('server info'.upper())
        print('\tusers count: {}'.format(len(get_table(self.conn, 'users_info'))).upper())

    def add_user(self, username, password):
        # add user to dictionary
        # self.users.update({username: password})
        # add user to 'users.csv'
        # with open('users.csv', 'a+') as write_obj:
        #     csv_writer = csv.writer(write_obj)
        #     csv_writer.writerow([username, password])

        insert_into_table(self.conn, 'users_info', 'username, password', (username, password))

    def send_message_to_client(self, c, message):
        c.send(message.upper().encode('utf-8'))

    def delete_user(self, username):
        delete_user_from_database(self.conn, username)

    # TODO: a single user cannot send message to server. I don'r know where the problem is
    def run_server(self):
        delete_user_from_database(self.conn, 'amir')
        # next create a socket object
        s = socket.socket()
        port = 12345

        # Next bind to the port
        # we have not typed any ip in the ip field
        # instead we have inputted an empty string
        # this makes the server listen to requests
        # coming from other computers on the network
        s.bind(('', port))
        s.listen(15)

        while True:
            print('- ' * 20)

            self.print_server_info()
            # print(self.users)

            # Establish connection with client.
            # print('{} users are connected to the server'.format(len(self.users)).upper())

            print('waiting for clients...'.upper(), end='')
            c, addr = s.accept()

            try:
                # print('waiting for clients...'.upper(), end='')
                # c, addr = s.accept()
                received_message = c.recv(2048).decode('utf-8').split()
                command = received_message[0]

                print('new connection!'
                      '\n\ttype    :\t{}'
                      '\n\tfrom    :\t{}:{}'
                      '\n\tat      :\t{}'.format(command, addr[0], addr[1], datetime.datetime.now().strftime("%c")).upper())

                if command == 'login':
                    # if received_message[1] in self.users.keys():
                    username, password = received_message[1], received_message[2]

                    if check_if_user_exists(self.conn, username):
                        # if self.users[received_message[1]] == received_message[2]:
                        if check_password(self.conn, username, password):
                            # c.send('logged in successfully'.upper().encode('utf-8'))
                            self.send_message_to_client(c, 'logged in successfully')
                            print('\tstatus  :\tsuccessful'.upper())
                        else:
                            # c.send('wrong password!'.upper().encode('utf-8'))
                            self.send_message_to_client(c, 'wrong password!')
                            print('\tstatus  :\twrong password'.upper())
                    else:
                        # c.send('user does not exist'.upper().encode('utf-8'))
                        self.send_message_to_client(c, 'user does not exist')
                        print('\tstatus  :\tuser not found'.upper())

                if command == 'signup':
                    # if received_message[1] in self.users.keys():
                    username, password = received_message[1], received_message[2]

                    if check_if_user_exists(self.conn, username):
                        # c.send('user already exists!'.upper().encode('utf-8'))
                        self.send_message_to_client(c, 'user already exists!')
                        print('\tstatus  :\tuser already exist!'.upper())
                    else:
                        self.add_user(username, password)
                        # c.send('user created successfully'.upper().encode('utf-8'))
                        self.send_message_to_client(c, 'user created successfully')
                        print('\tstatus  :\tsuccessful'.upper())

                if command == 'delete-user':
                    username = received_message[1]
                    self.delete_user(username)
                    self.send_message_to_client(c, 'user deleted successfully')
                    print('\tstatus  :\tsuccessful'.upper())

            except Exception as e:
                print('oops...something went wrong:'.upper())
                print(e)
                # c.send('oops, something went wrong!'.upper().encode('utf-8'))
                self.send_message_to_client(c, 'oops, something went wrong!')
            # Close the connection with the client
        # c.close()


if __name__ == '__main__':
    server = Server()
    server.run_server()

# first of all import the socket library 
import socket
import datetime
import csv


class Server:
    def __init__(self):
        # retrieve users to a dictionary from a csv file
        with open('users.csv', mode='r') as infile:
            reader = csv.reader(infile)
            self.users = {rows[0]: rows[1] for rows in reader}

    def add_user(self, username, password):
        # add user to dictionary
        self.users.update({username: password})
        # add user to 'users.csv'
        with open('users.csv', 'a+') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerow([username, password])

    def send_message_to_client(self, c, message):
        c.send(message.upper().encode('utf-8'))

    def run_server(self):
        # next create a socket object
        s = socket.socket()
        # print("Socket successfully created")

        # reserve a port on your computer in our
        # case it is 12345 but it can be anything
        port = 12345

        # Next bind to the port
        # we have not typed any ip in the ip field
        # instead we have inputted an empty string
        # this makes the server listen to requests
        # coming from other computers on the network
        s.bind(('', port))
        # print("socket binded to %s" % (port))

        # put the socket into listening mode
        s.listen(15)
        # print("socket is listening")

        # a forever loop until we interrupt it or
        # an error occurs
        while True:
            print('- '*20)
            print(self.users)

            # Establish connection with client.
            print('{} users are connected to the server'.format(len(self.users)).upper())

            print('waiting for clients...'.upper(), end='')
            c, addr = s.accept()

            try:
                # print('waiting for clients...'.upper(), end='')
                # c, addr = s.accept()
                received_message = c.recv(2048).decode('utf-8').split()

                print('new connection!'
                      '\n\ttype    :\t{}'
                      '\n\tfrom    :\t{}:{}'
                      '\n\tat      :\t{}'.format(received_message[0], addr[0], addr[1], datetime.datetime.now().strftime("%c")).upper())

                if received_message[0] == 'login':
                    if received_message[1] in self.users.keys():
                        if self.users[received_message[1]] == received_message[2]:
                            c.send('logged in successfully'.upper().encode('utf-8'))
                            print('\tstatus  :\tsuccessful'.upper())
                        else:
                            c.send('wrong password!'.upper().encode('utf-8'))
                            print('\tstatus  :\twrong password'.upper())
                    else:
                        c.send('user does not exist'.upper().encode('utf-8'))
                        print('\tstatus  :\tuser not found'.upper())

                if received_message[0] == 'signup':
                    if received_message[1] in self.users.keys():
                        c.send('user already exists!'.upper().encode('utf-8'))
                        print('\tstatus  :\tuser already exist!'.upper())
                    else:
                        self.add_user(received_message[1], received_message[2])
                        c.send('user created successfully'.upper().encode('utf-8'))
                        print('\tstatus  :\tsuccessful'.upper())
            except Exception as e:
                print('oops...something went wrong:'.upper())
                print(e)
                c.send('oops, something went wrong!'.upper().encode('utf-8'))
            # Close the connection with the client
        # c.close()


if __name__ == '__main__':
    server = Server()
    server.run_server()

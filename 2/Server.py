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
        git_database = "user_info.sql"
        self.conn_db = create_connection(git_database)
        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_passwords (
                                                    username text PRIMARY KEY,
                                                    password text
                                                ); """

        if self.conn_db is not None:
            create_table(self.conn_db, create_user_table_query)
        else:
            print("Error... Database is NOT active!")

        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_repositories (
                                                        username text,
                                                        repo_name text,
                                                        prvt_or_pblc text,
                                                        contributor text, 
                                                        CONSTRAINT PK_user PRIMARY KEY (username,repo_name)
                                                    ); """

        if self.conn_db is not None:
            create_table(self.conn_db, create_user_table_query)
        else:
            print("Error... Database is NOT active!")

    def print_server_info(self):
        print('server info'.upper())
        print('\tnumber of users in database: {}'.format(len(get_table(self.conn_db, 'users_passwords'))).upper())
        print('\tnumber of active users: {}'.format(len(self.active_users)).upper())
        [print('\t\t- {}'.format(i)) for i in self.active_users]

    def add_user(self, c,  username, password):
        insert_into_table(self.conn_db, 'users_passwords', 'username, password', (username, password))
        self.send_message_to_client(c, 'user created successfully'.upper())
        print('\tstatus  :\tsuccessful'.upper())
        self.active_users.append(username)
        make_directory(username, self.WORKING_DIRECTORY)

    def add_repo(self, c, username, repo_name, prvt_or_pblc):
        """
        at first, the user (username) is the only collaborator of
        the repository
        :param username:
        :param repo_name:
        :param prvt_or_pblc:
        :return:
        """
        insert_into_table(self.conn_db, 'users_repositories',
                          'username, repo_name, prvt_or_pblc, contributor',
                          (username, repo_name, prvt_or_pblc, username))

        parent_directory = os.path.join(self.WORKING_DIRECTORY, username)
        make_directory(repo_name, parent_directory)
        print('\tstatus  :\tREPOSITORY \"{}\" ({}) CREATED FOR USER \"{}\"'.format(repo_name, prvt_or_pblc, username))
        self.send_message_to_client(c, 'repository created successfully'.upper())

    def update_password(self, username, new_password):
        update_password(self.conn_db, new_password, username)

    def send_message_to_client(self, c, msg):
        # c.send(message.upper().encode('utf-8'))
        message = msg.encode(self.ENCODING)
        message_length = len(message)
        message_length = str(message_length).encode(self.ENCODING)
        message_length += b' ' * (self.MESSAGE_SIZE_LENGTH - len(message_length))
        c.send(message_length)
        c.send(message)

    def delete_user(self, username):
        delete_user_from_database(self.conn_db, username)

    # TODO : search file transfer
    def receive_file_from_client(self, ):
        pass

    # TODO : search file transfer
    def send_file_to_client(self, ):
        pass

    def handle_client(self, c, addr):
        # c.send(str.encode('Server is working:'))
        print('someone is connected!'.upper())
        connected = True
        while connected:
            try:
                print('- ' * 20)
                self.print_server_info()
                os.chdir(self.WORKING_DIRECTORY)
                print('waiting for clients...'.upper())
                message_length = int(c.recv(self.MESSAGE_SIZE_LENGTH).decode(self.ENCODING))
                received_message = c.recv(message_length).decode(self.ENCODING).split('`')
                command = received_message[0]
                print('new request!'
                      '\n\ttype    :\t[{}]'
                      '\n\tfrom    :\t{}:{}'
                      '\n\tat      :\t{}'.format(command, addr[0], addr[1],
                                                 datetime.datetime.now().strftime("%c")).upper())

                # login
                if command == 'login':
                    username, password = received_message[1], received_message[2]
                    if check_if_user_exists(self.conn_db, username):
                        if check_password(self.conn_db, username, password):
                            self.send_message_to_client(c, 'logged in successfully'.upper())
                            print('\tstatus  :\tsuccessful'.upper())
                            self.active_users.append(username)
                        else:
                            self.send_message_to_client(c, 'wrong password!'.upper())
                            print('\tstatus  :\twrong password'.upper())
                            connected = False
                    else:
                        self.send_message_to_client(c, 'user does not exist'.upper())
                        print('\tstatus  :\tuser not found'.upper())
                        connected = False

                # sign up
                elif command == 'signup':
                    username, password = received_message[1], received_message[2]
                    if check_if_user_exists(self.conn_db, username):
                        self.send_message_to_client(c, 'user already exists!'.upper())
                        print('\tstatus  :\tuser already exist!'.upper())
                        connected = False
                    else:
                        self.add_user(c, username, password)

                # delete user
                elif command == 'delete-user':
                    username = received_message[1]
                    self.delete_user(username)
                    self.send_message_to_client(c, 'user deleted successfully'.upper())
                    print('\tstatus  :\tsuccessful'.upper())
                    self.active_users.remove(username)
                    remove_directory(username, self.WORKING_DIRECTORY)
                    connected = False

                # create repository
                elif command == 'create-repo':
                    username, repository_name = received_message[1], received_message[2]
                    repository_name, privacy = repository_name.split('_')
                    self.add_repo(c, username, repository_name, privacy)


                # show repositories for a single user
                elif command == 'show-repo':
                    username = received_message[1]
                    repositories = os.listdir(os.path.join(self.WORKING_DIRECTORY, username))
                    self.send_message_to_client(c, str(len(repositories)))
                    for repo in repositories:
                        self.send_message_to_client(c, '   - '+repo)

                # push
                # TODO : create a table in database
                elif command == 'push':
                    username = received_message[1]
                    repo = received_message[2]
                    file_name = received_message[3]
                    file_size = received_message[4]
                    file_content = received_message[5]
                    print('\tUSERNAME:\t{}'.format(username))
                    print('\tREPO.   :\t{}'.format(repo))
                    print('\tF.NAME  :\t{}'.format(file_name))
                    print('\tF.SIZE  :\t{}'.format(file_size))
                    try:
                        path = os.path.join(self.WORKING_DIRECTORY, username)
                        path = os.path.join(path, repo)
                        os.chdir(path)
                        file = open(file_name, 'w')
                        file.write(file_content)
                        self.send_message_to_client(c, 'FILE {} IS PUSHED TO SERVER'.format(file_name))
                        file.close()
                        print('\tstatus  :\tsuccessful'.upper())
                    except Exception as e:
                        print('\tSTATUS  :\t{}'.format(e))
                        self.send_message_to_client(c, '!!! ERROR FOR PUSHING {}'.format(file_name))


                # show all users
                elif command == 'show-users':
                    # list all users from database for client
                    username = received_message[1]
                    users = list(get_table(self.conn_db, 'users_passwords'))
                    for r in users:
                        if r[0] == username:
                            users.remove(r)

                    self.send_message_to_client(c, str(len(users)))
                    response = ''
                    i = 1
                    for r in users:
                        response += '   {} - {}'.format(i, r[0])
                        i += 1
                    self.send_message_to_client(c, response)

                # add contributor
                elif command == 'add-contributor':
                    # after "show-users"...
                    username = received_message[1]
                    target_repo = received_message[2]
                    choice_of_client = received_message[3]

                    users = list(get_table(self.conn_db, 'users_passwords'))
                    for r in users:
                        if r[0] == username:
                            users.remove(r)

                    if username == '%cancel%':
                        print('\tstatus  :\tCANCELED')
                    else:
                        contributor = users[int(choice_of_client) - 1][0]

                        cur = self.conn_db.cursor()
                        cur.execute("SELECT contributor FROM users_repositories WHERE username=? and repo_name=?", (username,target_repo))
                        old_contributor = cur.fetchall()[0][0]

                        new_contributor = old_contributor + " " + contributor
                        print(old_contributor, contributor, '-', new_contributor)
                        update_contributor(self.conn_db, new_contributor, target_repo, username)

                        print('\tstatus  :\t{} IS NOW A CONTRIBUTOR OF {}'.format(contributor, target_repo))

                        # copy file from source to contributor
                        try:
                            src = os.path.join(self.WORKING_DIRECTORY, os.path.join(username, target_repo))
                            dest = os.path.join(self.WORKING_DIRECTORY, os.path.join(contributor, target_repo))
                            shutil.copytree(src, dest)
                            print('\t         \tCOPY PROCESS WAS SUCCESSFULLY')
                        except Exception as e:
                            print('\t         \t{}'.format(e))



                # show all repositories
                elif command == 'show-repo-all':
                    username = received_message[1]
                    repositories = list(get_table(self.conn_db, 'users_repositories'))

                    # filter the repositories for user (hide PRIVATE repositories if user is not a collaborator)
                    for r in repositories:
                        u_name, repo_name, p, collabs = r[0], r[1], r[2], r[3].split()
                        if p == 'PRVT' and username not in collabs:
                            repositories.remove(r)

                    self.send_message_to_client(c, str(len(repositories)))
                    for r in repositories:
                        u_name, repo_name, p, collabs = r[0], r[1], r[2], r[3].split()
                        if p == 'PRVT':
                            p = 'PRIVATE'
                        else:
                            p = 'PUBLIC'
                        record = '   - NAME: \"{}\"\n     PRVT/PBLC: {}\n     CONTRIBUTOR: {} \n'.format(repo_name, p, collabs)
                        self.send_message_to_client(c, record)


                    # self.send_message_to_client(c, str(len(repositories)))
                    # for repo in repositories:
                    #     self.send_message_to_client(c, '    - '+repo)

                # disconnecting
                elif command == 'disconnect':
                    username = received_message[1]
                    self.active_users.remove(username)
                    connected = False

                # change password
                elif command == 'change-password':
                    username = received_message[1]
                    new_password = received_message[2]
                    self.update_password(username, new_password)
                    print('\tstatus  :\tPASSWORD SUCCESSFULLY UPDATED FOR USER \"{}\"'.format(username))
                    self.send_message_to_client(c, 'password changed successfully'.upper())

                # wrong input
                else:
                    print('wrong input from client!'.upper())
            except Exception as e:
                print(e)
                print('\ttype    :\t{}'
                      '\n\tfrom    :\t{}:{}'
                      '\n\tat      :\t{}'.format('CONNECTION-LOST', addr[0], addr[1],
                                                 datetime.datetime.now().strftime("%c")).upper())
                self.active_users.remove(username)
                connected = False

        print('- ' * 20)
        self.print_server_info()
        print('waiting for clients...'.upper())
        c.close()

    def run_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.ADDRESS, self.PORT))
        print('server is up...'.upper())
        s.listen()
        while True:
            connection, address = s.accept()
            th = threading.Thread(target=self.handle_client, args=(connection, address,))
            th.start()


if __name__ == '__main__':
    server = Server()
    server.run_server()

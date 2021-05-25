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
        git_database = "server_database.sql"
        self.conn_db = create_connection(git_database)

        # user password table
        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_passwords (
                                                    username text PRIMARY KEY,
                                                    password text
                                                ); """
        if self.conn_db is not None:
            create_table(self.conn_db, create_user_table_query)
        else:
            print("Error... Database is NOT active!")

        # user repositories table
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

        # user commits table
        create_user_table_query = """ CREATE TABLE IF NOT EXISTS users_commits (
                                                                        username text,
                                                                        repository text,
                                                                        file_path text,
                                                                        file_content text,
                                                                        message text, 
                                                                        commit_time text
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

    def add_user(self, c, username, password):
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

        # initial commit
        insert_into_table(self.conn_db, 'users_commits',
                          'username, repository, file_path, file_content, message, commit_time',
                          (username, repo_name, '', '', 'initial_commit', datetime.datetime.now()))

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

    def get_owner(self, repo, username, ):
        """
        find tho owner of a repo
        :param repo:
        :param username:
        :return: owner
        """
        cur = self.conn_db.cursor()
        q = "SELECT contributor FROM users_repositories WHERE repo_name = \'{}\'" \
            .format(repo)
        cur.execute(q)
        contributors = cur.fetchall()
        owner = username
        for cc in contributors:
            list_of_contrinutors = cc[0].split()
            if username in list_of_contrinutors:
                owner = cc[0][0]
        return owner

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
                            if username in self.active_users:
                                self.send_message_to_client(c, 'you are logged in from another location'.upper())
                                print('\tstatus  :\talready logged in'.upper())
                            else:
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
                        self.send_message_to_client(c, '   - ' + repo)


                elif command == 'check-synchronization':
                    username = received_message[1]
                    repo = received_message[2]

                    # fine the owner
                    owner = self.get_owner(repo, username)

                    try:
                        # get last commit time
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT DISTINCT commit_time FROM {} WHERE username = \'{}\' ORDER BY commit_time"
                                    .format('users_commits', username))
                        last_commit_time = cur.fetchall()[-1][0]

                        cur = self.conn_db.cursor()
                        q = "SELECT * FROM {} WHERE repository = \'{}\' and commit_time = \'{}\' and username = \'{}\'" \
                            .format('users_commits', repo, last_commit_time, username)
                        cur.execute(q)
                        files = cur.fetchall()

                        self.send_message_to_client(c, str(len(files)))

                        for f in files:
                            self.send_message_to_client(c, f[2])
                            self.send_message_to_client(c, f[3])

                    except IndexError:
                        # get last commit time
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT DISTINCT commit_time FROM {} WHERE username = \'{}\' ORDER BY commit_time"
                                    .format('users_commits', owner))
                        last_commit_time = cur.fetchall()[-1][0]

                        cur = self.conn_db.cursor()
                        q = "SELECT * FROM {} WHERE repository = \'{}\' and commit_time = \'{}\' and username = \'{}\'" \
                            .format('users_commits', repo, last_commit_time, owner)
                        cur.execute(q)
                        files = cur.fetchall()

                        self.send_message_to_client(c, str(len(files)))

                        for f in files:
                            self.send_message_to_client(c, f[2])
                            self.send_message_to_client(c, f[3])






                # get commits from users database and add to server commit table
                elif command == 'commit':
                    username = received_message[1]
                    repository = received_message[2]
                    file_path = received_message[3]
                    file_content = received_message[4]
                    message = received_message[5]
                    time = received_message[6]

                    try:
                        insert_into_table(self.conn_db, 'users_commits',
                                          'username, repository, file_path, file_content, message, commit_time',
                                          (username, repository, file_path, file_content, message, time))
                    except Exception as e:
                        print(e)

                    self.send_message_to_client(c, 'FILE {} FROM COMMIT \"{}\" IS RECEIVED'.format(file_path, message))
                    print('\tSTATUS  :\tFILE \"{}\" FROM COMMIT \"{}\", USER \"{}\" AND REPO \"{}\" ADDED TO DATABASE'
                          .format(file_path, message, username, repository))

                # push
                elif command == 'push':
                    username = received_message[1]
                    repo = received_message[2]
                    last_commit_time = received_message[3]

                    # check if we are the contributor
                    owner = self.get_owner(repo, username)

                    cur = self.conn_db.cursor()
                    q = "SELECT * FROM {} WHERE repository = \'{}\' and commit_time = \'{}\' and username = \'{}\'" \
                        .format('users_commits', repo, last_commit_time, username)
                    cur.execute(q)
                    files = cur.fetchall()
                    self.send_message_to_client(c, str(len(files)))
                    parent_path = os.path.join(self.WORKING_DIRECTORY, owner)
                    make_directory(repo, parent_path)
                    parent_path = os.path.join(parent_path, repo)
                    os.chdir(parent_path)
                    remove_directory_contents(parent_path)

                    print('\tSTATUS  :\t')
                    for f in files:
                        try:
                            parent_path = os.path.join(self.WORKING_DIRECTORY, owner)
                            parent_path = os.path.join(parent_path, repo)
                            os.chdir(parent_path)
                            sub_directories = f[2].split('\\')
                            if len(sub_directories) == 1:
                                file = open(f[2], 'w')
                                file.write(f[3])
                                file.close()

                            else:
                                for i in range(len(sub_directories) - 1):
                                    make_directory(sub_directories[i], parent_path)
                                    parent_path = os.path.join(parent_path, sub_directories[i])
                                    os.chdir(parent_path)
                                file = open(sub_directories[-1], 'w')
                                file.write(f[3])
                                file.close()
                            self.send_message_to_client(c, 'FILE {} IS PUSHED TO SERVER'.format(f[2]))
                            print('\t         \t{} PUSHED SUCCESSFULLY TO {}'.format(f[2], parent_path))
                            # print('\t         \tCONTENT: {}'.format(f[3]))
                            file.close()
                        except Exception as e:
                            print('\t         \t{}'.format(e))
                            self.send_message_to_client(c, '!!! ERROR FOR PUSHING {}'.format(f[2]))

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
                        response += '   {} - {}\n'.format(i, r[0])
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
                        cur.execute("SELECT contributor FROM users_repositories WHERE username=? and repo_name=?",
                                    (username, target_repo))
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
                    i = 1
                    for r in repositories:
                        u_name, repo_name, p, collabs = r[0], r[1], r[2], r[3].split()
                        if p == 'PRVT':
                            p = 'PRIVATE'
                        else:
                            p = 'PUBLIC'
                        record = '   {} - NAME: \"{}\"\n     PRVT/PBLC: {}\n     CONTRIBUTOR:\n'.format(i,
                                                                                                        repo_name,
                                                                                                        p)
                        is_owner = True
                        for collab in collabs:
                            record += '     |- {}'.format(collab)
                            if is_owner:
                                record += ' (OWNER)\n'
                            else:
                                record += '\n'
                            is_owner = False
                        self.send_message_to_client(c, record)
                        i += 1

                # show all commits
                elif command == 'show-commits':
                    username = received_message[1]
                    repo = received_message[2]

                    cur = self.conn_db.cursor()
                    q = "SELECT commit_time, message from users_commits WHERE repository = \'{}\' and username = \'{}\' ORDER BY commit_time" \
                        .format(repo, username)
                    cur.execute(q)
                    times = cur.fetchall()
                    tt = []
                    mm = []
                    for t in times:
                        tt.append(t[0])
                        mm.append(t[1])

                    self.send_message_to_client(c, str(len(tt)))

                    for t, m in zip(tt, mm):
                        self.send_message_to_client(c, 'TIME    : {}\n'
                                                       'MESSAGE : \"{}\"'.format(t, m))
                        cur = self.conn_db.cursor()
                        q = "SELECT file_path from users_commits WHERE repository = \'{}\' and username = \'{}\'and commit_time = \'{}\'" \
                            .format(repo, username, t)
                        cur.execute(q)
                        files = cur.fetchall()

                        self.send_message_to_client(c, str(len(files)))
                        for ff in files:
                            self.send_message_to_client(c, '    {}'.format(ff[0]))



                # pull a specific repository
                elif command == 'pull-my-repo':
                    username = received_message[1]
                    repo = received_message[2]

                    cur = self.conn_db.cursor()
                    q = "SELECT commit_time from users_commits WHERE repository = \'{}\' and username = \'{}\'" \
                        .format(repo, username)
                    cur.execute(q)
                    times = cur.fetchall()
                    tt = []
                    for t in times:
                        tt.append(t[0])

                    last_push_time = max(tt)

                    cur = self.conn_db.cursor()
                    q = "SELECT * FROM {} WHERE commit_time = \'{}\'" \
                        .format('users_commits', last_push_time)
                    cur.execute(q)
                    pull_list = cur.fetchall()
                    self.send_message_to_client(c, str(len(pull_list)))
                    for p in pull_list:
                        record = '{}`{}`{}'.format(p[1], p[2], p[3])
                        print('\tstatus  :\tPULLING \"{}\"'.format(p[2]))
                        self.send_message_to_client(c, record)

                # pull a repository from main menu
                elif command == 'pull-a-repo':
                    username = received_message[1]
                    index = int(received_message[2])

                    repositories = list(get_table(self.conn_db, 'users_repositories'))

                    # filter the repositories for user (hide PRIVATE repositories if user is not a collaborator)
                    for r in repositories:
                        u_name, repo_name, p, collabs = r[0], r[1], r[2], r[3].split()
                        if p == 'PRVT' and username not in collabs:
                            repositories.remove(r)
                    print(repositories)
                    selected_repo = repositories[index - 1]
                    u_name, repo_name = selected_repo[0], selected_repo[1]
                    cur = self.conn_db.cursor()

                    q = "SELECT commit_time from users_commits WHERE repository = \'{}\' and username = \'{}\'"\
                        .format(repo_name, u_name)
                    cur.execute(q)
                    times = cur.fetchall()
                    tt = []
                    for t in times:
                        tt.append(t[0])


                    last_push_time = max(tt)


                    cur = self.conn_db.cursor()
                    q = "SELECT * FROM {} WHERE commit_time = \'{}\'" \
                        .format('users_commits', last_push_time)
                    cur.execute(q)
                    pull_list = cur.fetchall()
                    self.send_message_to_client(c, str(len(pull_list)))
                    for p in pull_list:
                        record = '{}`{}`{}'.format(p[1], p[2], p[3])
                        print('\tstatus  :\tPULLING \"{}\"'.format(p[2]))
                        self.send_message_to_client(c, record)

                # disconnecting
                elif command == 'disconnect':
                    username = received_message[1]
                    self.active_users.remove(username)
                    self.send_message_to_client(c, "YOU ARE DISCONNECTED FROM SERVER")
                    connected = False

                # change password
                elif command == 'change-password':
                    username = received_message[1]
                    new_password = received_message[2]
                    self.update_password(username, new_password)
                    print('\tSTATUS  :\tPASSWORD SUCCESSFULLY UPDATED FOR USER \"{}\"'.format(username))
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

import socket
import getpass
import os
import datetime
import shutil
from colorama import Fore, Back, Style
import sqlite3
from sqlite3 import Error
from tqdm import tqdm


def copy_directory(src, dst):
    shutil.copytree(src, dst, copy_function=shutil.copy)


def get_table(conn, table):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :param table: table name
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM {}".format(table))
    return cur.fetchall()


def insert_into_table(conn_user_password, table, fields, values):
    """
    Create a new task
    :param conn_user_password:
    :param table: table name
    :param values: records
    :param fields: columns
    :return:
    """
    question_marks = '?'
    for i in range(len(values)-1):
        question_marks += ',?'

    sql = ''' INSERT INTO {}({})
              VALUES({}) '''.format(table, fields, question_marks)
    cur = conn_user_password.cursor()
    try:
        cur.execute(sql, values)
        conn_user_password.commit()
    except Exception as e:
        print(e)
    return cur.lastrowid


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def hr():
    print('-'*60)


def make_directory(new_folder_name, parent_directory):
    try:
        path = os.path.join(parent_directory, new_folder_name)
        os.mkdir(path)
        print('DIRECTORY \"{}\" CREATED'.format(new_folder_name))
    except Exception as e:
        print(e)


def remove_directory(target_folder_name, parent_directory):
    try:
        path = os.path.join(parent_directory, target_folder_name)
        os.rmdir(path)
        print('DIRECTORY \"{}\" removed'.format(target_folder_name))
    except Exception as e:
        print(e)
        path = os.path.join(parent_directory, target_folder_name)
        shutil.rmtree(path)


class Client:
    def __init__(self):
        self.PORT = 12345
        self.ADDRESS = socket.gethostbyname(socket.gethostname())
        self.MESSAGE_SIZE_LENGTH = 64
        self.ENCODING = 'utf-8'
        self.username = "???????"

        self.ROOT_PATH = os.getcwd()
        self.current_directory = self.ROOT_PATH

        # creating database connection
        git_database = "client_database.sql"
        conn_user_password = None
        try:
            conn_user_password = sqlite3.connect(git_database, check_same_thread=False)
            self.conn_db = conn_user_password
        except Error as e:
            print(e)
        self.conn_db = conn_user_password

        # create commits table
        create_user_table_query = """ CREATE TABLE IF NOT EXISTS commits (
                                                                repository text,
                                                                file_path text,
                                                                file_content text,
                                                                message text, 
                                                                commit_time text, 
                                                                CONSTRAINT PK_commit PRIMARY KEY (file_path, commit_time)
                                                            ); """
        if self.conn_db is not None:
            try:
                c = self.conn_db.cursor()
                c.execute(create_user_table_query)
            except Error as e:
                print(e)
        else:
            print("Error... Database is NOT active!")

    def receive_message_from_server(self, c, print_it):
        message_length = int(c.recv(self.MESSAGE_SIZE_LENGTH).decode(self.ENCODING))
        received_message = c.recv(message_length).decode(self.ENCODING)
        if print_it:
            print(Fore.YELLOW + received_message + Fore.WHITE)
        return received_message

    # TODO : search file transfer
    def receive_file_from_server(self, ):
        pass

    # TODO : search file transfer
    def send_file_to_server(self, ):
        pass

    def send_message(self, client, msg):
        message = msg.encode(self.ENCODING)
        message_length = len(message)
        message_length = str(message_length).encode(self.ENCODING)
        message_length += b' ' * (self.MESSAGE_SIZE_LENGTH - len(message_length))
        client.send(message_length)
        client.send(message)

    def commit(self, files, repo, message, time):
        if not files:
            insert_into_table(self.conn_db, 'commits',
                              'repository, file_path, file_content, message, commit_time',
                              (repo, '', '', message, time))

        for file_name in tqdm(files, desc="COMMITTING FILES"):
            file_content = open(file_name, 'r')
            path = os.path.relpath(file_name)

            # insert commit tp database
            insert_into_table(self.conn_db, 'commits',
                              'repository, file_path, file_content, message, commit_time',
                              (repo, path, file_content.read(), message, time))
        print('FILES ARE ADDED TO LOCAL DATABASE.')

    def print_commits(self, commits, old, new):
        print(' * USERNAME  : {}\n'
              ' | REPOSITORY: {}\n'
              ' | MESSAGE   : {}\n'
              ' | TIME      : {}'.format(self.username, commits[0][0], commits[0][3], commits[0][4]))
        print(' | FILES')
        for c in commits:
            print(' |-', Fore.CYAN, c[1], Fore.WHITE)
        print(' | DIFFERENCES FROM LAST COMMIT')
        green = new - old
        yellow = new & old
        red = old - new

        for g in green:
            if g != '':
                print(' |-', Fore.GREEN, '[+]', g[0], Fore.WHITE)
        for y in yellow:
            if y != '':
                print(' |-', Fore.YELLOW, '[*]', y[0], Fore.WHITE)
        for r in red:
            if r != '':
                print(' |-', Fore.RED, '[-]', r[0], Fore.WHITE)

    def manage_repository(self, s,  repo, repo_dir):
        while True:
            try:
                hr()
                print(Fore.LIGHTBLACK_EX, 'current directory:'.upper(), self.current_directory, Fore.WHITE)
                print('repository: '.upper(), repo)
                option = int(input('please select an option\n'
                                   ' 1 - commit\n'
                                   ' 2 - push to server\n'
                                   ' 3 - pull this repository from server\n'
                                   ' 4 - add contributor\n'
                                   ' 5 - show all pending commits (local)\n'
                                   '-1 - back to menu\n'
                                   ' > '.upper()))
                # main menu
                if option == -1:
                    return

                # commit
                elif option == 1:
                    time = datetime.datetime.now()
                    files = os.listdir(self.current_directory)

                    commit_it = False
                    message = input('INSERT COMMIT MESSAGE: (-1 TO CANCEL)\n > ')
                    if message != '-1':
                        commit_it = True
                    if commit_it:
                        self.commit(files, repo, message, time)
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT * FROM {} WHERE commit_time = \'{}\'".format('commits', time))
                        new_commits = cur.fetchall()

                        # get times
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT DISTINCT commit_time FROM {} ORDER BY commit_time".format('commits'))
                        times = cur.fetchall()
                        # new commit
                        cur = self.conn_db.cursor()
                        cur.execute(
                            "SELECT file_path FROM {} WHERE commit_time = \'{}\'".format('commits', times[-1][0]))
                        # print(cur.fetchall())
                        last_commit = set(cur.fetchall())

                        # last commit
                        cur = self.conn_db.cursor()
                        cur.execute(
                            "SELECT file_path FROM {} WHERE commit_time = \'{}\'".format('commits', times[-2][0]))
                        # print(cur.fetchall())
                        before_last_commit = set(cur.fetchall())
                        # self.print_commifs_diff(old=before_last_commit, new=last_commit)
                        self.print_commits(commits=new_commits, old=before_last_commit, new=last_commit)

                    else:
                        print(Fore.RED, 'CANCELED!', Fore.WHITE)

                # TODO send from database not local
                # push
                elif option == 2:
                    # send commits to server's commit database:
                    cur = self.conn_db.cursor()
                    cur.execute("SELECT * FROM {} WHERE repository = \'{}\'".format('commits', repo))
                    commits = cur.fetchall()
                    if commits:
                        # print(Fore.GREEN, end='')
                        for commit in tqdm(commits, desc="SENDING COMMITS TO SERVER'S DATABASE"):
                            msg = 'commit`{}`{}`{}`{}`{}`{}'.format(self.username,
                                                                    commit[0],
                                                                    commit[1],
                                                                    commit[2],
                                                                    commit[3],
                                                                    commit[4])
                            self.send_message(s, msg)
                            self.receive_message_from_server(s, print_it=False)

                        # push last commit contents to the server
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT DISTINCT commit_time FROM {} ORDER BY commit_time".format('commits'))
                        last_commit_time = cur.fetchall()[-1]

                        msg = 'push`{}`{}`{}'.format(self.username, repo, last_commit_time[0])
                        self.send_message(s, msg)
                        n = self.receive_message_from_server(s, print_it=False)
                        for i in tqdm(range(int(n)), desc='PUSH TO SERVER DIRECTORIES'):
                            self.receive_message_from_server(s, print_it=False)

                        # clear local database for this repositories' commits
                        sql = "DELETE FROM commits where repository = \'{}\'".format(repo)
                        cur = self.conn_db.cursor()
                        cur.execute(sql)
                        self.conn_db.commit()
                        print('RECORDS FOR REPOSITORY \"{}\" REMOVED FROM LOCAL DATABASE'.format(repo))
                        print(Fore.WHITE, end='')
                    else:
                        print(Fore.RED, 'NO COMMITS FOUNDED!', Fore.WHITE)
                # pull
                elif option == 3:
                    pass

                # add contributor
                elif option == 4:
                    """
                    FRIENDLY REMINDER:
                    in users_repositories table, the "Contributor" format is a string like this:
                    'OWNER Contributor1 Contributor2 ... ContributorN'
                    """
                    msg = 'show-users`{}'.format(self.username)
                    self.send_message(s, msg)
                    user_count = int(self.receive_message_from_server(s, print_it=False))
                    self.receive_message_from_server(s, print_it=True)

                    while True:
                        try:
                            # asking server to show us all the users
                            print(user_count)
                            choice = int(input('> SELECT A NUMBER (-1 to cancel): '))

                            if 1 <= choice <= user_count:
                                msg2 = 'add-contributor`{}`{}`{}'.format(self.username, repo, choice)
                                self.send_message(s, msg2)
                                break
                            elif choice == -1:
                                self.send_message(s, 'add-contributor %cancel% x x')
                                break
                            else:
                                print(Fore.RED, 'bad input! try again', Fore.WHITE)
                        except Exception as e:
                            print(Fore.RED, 'bad input! try again', Fore.WHITE)
                            print(e)

                # show all commits local
                elif option == 5:
                    cur = self.conn_db.cursor()
                    cur.execute("SELECT DISTINCT commit_time FROM {} ORDER BY commit_time".format('commits'))
                    times = cur.fetchall()
                    file_names = []

                    for c in range(len(times)):
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT file_path FROM {} WHERE commit_time = \'{}\'".format('commits', times[c][0]))
                        file_names.append(set(cur.fetchall()))

                    for c in range(len(times)):
                        cur = self.conn_db.cursor()
                        cur.execute("SELECT * FROM {} WHERE commit_time = \'{}\'".format('commits', times[c][0]))
                        cc = cur.fetchall()
                        if c == 0:
                            self.print_commits(commits=cc, old=set([]), new=file_names[c])
                        else:
                            self.print_commits(commits=cc, old=file_names[c - 1], new=file_names[c])
                        print()
            except Exception as e:
                if e == 'list index out of range':
                    pass
                else:
                    print(e)

    def main(self):
        # global username
        cls()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flag = False  # a boolean variable to configure if the user can use the service or not

        print('connecting to server...'.upper())
        try:
            s.connect((self.ADDRESS, self.PORT))
            print(Fore.GREEN, 'connected to the server!'.upper(), Fore.WHITE)
        except ConnectionRefusedError:
            print(Fore.RED, 'server not found :('.upper(), Fore.WHITE)
            quit()

        option = int(input('select an option\n'
                           ' 1 - login\n'
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
                # password = input(' > password:  '.upper())
                password = getpass.getpass(' > password:  '.upper())
                msg = 'login`{}`{}'.format(username, password)

                self.send_message(s, msg)
                received_message = self.receive_message_from_server(s, print_it=True)
                if received_message == 'logged in successfully'.upper():
                    flag = True
                    self.username = username

            # creating a new account
            elif option == 2:
                print('new account:'.upper())
                username = input(' > username:  '.upper())
                # password = input(' > password:  '.upper())
                password = getpass.getpass(' > password:  '.upper())
                msg = 'signup`{}`{}'.format(username, password)

                self.send_message(s, msg)
                received_message = self.receive_message_from_server(s, print_it=True)
                if received_message == 'user created successfully'.upper():
                    flag = True
                    self.username = username

            else:
                print('wrong input!'.upper())
        # cls()
        if not flag:
            print('connection closed\nplease try again later'.upper())
        else:

            while True:
                try:
                    hr()
                    print(Fore.LIGHTBLACK_EX,  'current directory:'.upper(), self.current_directory, Fore.WHITE)
                    option = int(input('please select an option\n'
                                       ' 1 - create repository\n'
                                       ' 2 - show my repositories (local)\n'
                                       ' 3 - show my repositories (server)\n'
                                       ' 4 - show all repositories (server)\n'
                                       ' 5 - select repository\n'
                                       ' 6 - update password\n'
                                       ' 7 - delete user\n'
                                       ' 8 - pull a repository\n'
                                       '-1 - disconnect from server\n'
                                       ' > '.upper()))

                    # disconnect
                    if option == -1:
                        if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                            msg = 'disconnect`{}'.format(self.username)
                            self.send_message(s, msg)
                            s.close()
                            break  # end of program

                    # create repository
                    elif option == 1:
                        repository_name = input(' > repository name:  '.upper())
                        while True:
                            prvt_or_pblc = input(' > private(0) or public(1)? : '.upper())

                            if prvt_or_pblc == '0':
                                prvt_or_pblc = 'PRVT'
                                break
                            elif prvt_or_pblc == '1':
                                prvt_or_pblc = 'PBLC'
                                break
                            else:
                                print(Fore.RED, 'bad input! try again', Fore.WHITE)

                        pth = self.ROOT_PATH
                        make_directory(repository_name, pth)

                        msg = 'create-repo`{}`{}_{}'.format(self.username, repository_name, prvt_or_pblc)
                        self.send_message(s, msg)
                        self.receive_message_from_server(s, print_it=True)

                    # show repositories (local)
                    elif option == 2:
                        repositories = os.listdir(self.ROOT_PATH)
                        repositories.remove('Client.py')
                        repositories.remove('client_database.sql')
                        for repo in repositories:
                            print('\t - ' + repo)

                    # show repositories (server)
                    elif option == 3:
                        msg = 'show-repo`{}'.format(self.username)
                        self.send_message(s, msg)
                        n = int(self.receive_message_from_server(s, print_it=False))
                        for i in range(n):
                            self.receive_message_from_server(s, print_it=True)
                        print()

                    # show all repositories
                    elif option == 4:
                        msg = 'show-repo-all`{}'.format(self.username)
                        self.send_message(s, msg)
                        n = int(self.receive_message_from_server(s, print_it=False))
                        for i in range(n):
                            self.receive_message_from_server(s, print_it=True)
                        print()

                    # select repository
                    elif option == 5:
                        repositories = os.listdir(self.ROOT_PATH)
                        repositories.remove('Client.py')
                        repositories.remove('client_database.sql')
                        while True:
                            print('select a number (enter \"Q\" to cancel)'.upper())
                            c = 1
                            for repo in repositories:
                                print(' {} - '.format(c) + repo)
                                c += 1
                            n = input(' > ')
                            if n == 'Q':
                                print('canceled!'.upper())
                                break
                            else:
                                try:
                                    if 1 <= int(n) <= c:
                                        current_repository = repositories[int(n) - 1]
                                        print(Fore.GREEN, 'REPOSITORY \"{}\" SELECTED!'.format(current_repository), Fore.WHITE)
                                        self.current_directory = os.path.join(self.ROOT_PATH, current_repository)
                                        os.chdir(self.current_directory)
                                        self.manage_repository(s, current_repository, self.current_directory)
                                        self.current_directory = self.ROOT_PATH
                                        # os.chdir(self.current_directory)
                                        break
                                    else:
                                        print(Fore.RED, 'please enter a valid input'.upper(), Fore.WHITE)
                                except:
                                    print(Fore.RED, 'please enter a valid input'.upper(), Fore.WHITE)

                    # update password
                    elif option == 6:
                        new_password = getpass.getpass(' > enter new password:  '.upper())
                        confirm_new_password = getpass.getpass(' > confirm new password:  '.upper())
                        if new_password == confirm_new_password:
                            msg = 'change-password`{}`{}'.format(self.username, new_password)
                            self.send_message(s, msg)
                            self.receive_message_from_server(s, print_it=True)
                        else:
                            print(Fore.RED, '   passwords did\'nt match, try again'.upper(), Fore.WHITE)

                    # delete user
                    elif option == 7:
                        if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                            msg = 'delete-user`{}'.format(self.username)
                            self.send_message(s, msg)
                            self.receive_message_from_server(s, print_it=True)
                            s.close()

                            # clear local database
                            sql = 'DELETE FROM commits'
                            cur = self.conn_db.cursor()
                            cur.execute(sql)
                            self.conn_db.commit()

                            break  # end of program

                    # pull a repository from main menu
                    elif option == 8:
                        msg = 'show-repo-all`{}'.format(self.username)
                        self.send_message(s, msg)
                        n = int(self.receive_message_from_server(s, print_it=False))
                        for i in range(n):
                            self.receive_message_from_server(s, print_it=True)

                        choice = int(input('select a repository (-1 to cancel)'.upper()))
                        if choice == -1:
                            print(Fore.RED, 'CANCELED!', Fore.WHITE)
                        else:
                            msg = 'pull-a-repo`{}`{}'.format(self.username, choice)
                            self.send_message(s, msg)
                            n = int(self.receive_message_from_server(s, print_it=False))
                            for i in tqdm(range(n), desc='PULL FROM SERVER'):
                                repo, path, data = self.receive_message_from_server(s, print_it=True).split('`')
                                make_directory(repo, self.ROOT_PATH)
                                parent = os.path.join(self.ROOT_PATH, repo)
                                os.chdir(parent)
                                file = open(path, 'w')
                                file.write(data)
                                print(Fore.YELLOW, '{} IS PULLED FROM SERVER.'.format(path), Fore.WHITE)
                                file.close()

                    # cls()
                except ValueError:
                    print(Fore.RED, 'bad input! try again', Fore.WHITE)


if __name__ == '__main__':
    c = Client()
    c.main()

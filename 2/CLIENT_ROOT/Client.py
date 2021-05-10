import socket
import getpass
import os
import shutil
from colorama import Fore, Back, Style

def copy_directory(src, dst):
    shutil.copytree(src, dst, copy_function=shutil.copy)

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
        pass


def remove_directory(target_folder_name, parent_directory):
    try:
        path = os.path.join(parent_directory, target_folder_name)
        os.rmdir(path)
        print('DIRECTORY \"{}\" removed'.format(target_folder_name))
    except Exception as e:
        # print(e)
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

    def manage_repository(self, repo, repo_dir):
        while True:
            hr()
            print(Fore.LIGHTBLACK_EX, 'current directory:'.upper(), self.current_directory, Fore.WHITE)
            print('repository: '.upper(), repo)
            option = int(input('please select an option\n'
                               ' 1 - commit\n'
                               ' 2 - push to server\n'
                               ' 3 - pull from server\n'
                               ' 4 - add contributor\n'
                               '-1 - back to menu\n'
                               ' > '.upper()))
            # main menu
            if option == -1:
                return

            # commit
            elif option == 1:
                pass

            # push
            elif option == 2:
                pass


            # pull
            elif option == 3:
                pass

            # add contributor
            elif option == 4:
                pass





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
                msg = 'login {} {}'.format(username, password)

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
                msg = 'signup {} {}'.format(username, password)

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
                                       '-1 - disconnect from server\n'
                                       ' > '.upper()))

                    # disconnect
                    if option == -1:
                        if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                            msg = 'disconnect {}'.format(self.username)
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

                        msg = 'create-repo {} {}_{}'.format(self.username, repository_name, prvt_or_pblc)
                        self.send_message(s, msg)
                        self.receive_message_from_server(s, print_it=True)

                    # show repositories (local)
                    elif option == 2:
                        repositories = os.listdir(self.ROOT_PATH)
                        repositories.remove('Client.py')
                        for repo in repositories:
                            print('\t - ' + repo)

                    # show repositories (server)
                    elif option == 3:
                        msg = 'show-repo {}'.format(self.username)
                        self.send_message(s, msg)
                        n = int(self.receive_message_from_server(s, print_it=False))
                        for i in range(n):
                            self.receive_message_from_server(s, print_it=True)
                        print()

                    # show all repositories
                    elif option == 4:
                        msg = 'show-repo-all'
                        self.send_message(s, msg)

                    # select repository
                    elif option == 5:
                        repositories = os.listdir(self.ROOT_PATH)
                        repositories.remove('Client.py')
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
                                        self.manage_repository(current_repository, self.current_directory)
                                        self.current_directory = self.ROOT_PATH
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
                            msg = 'change-password {} {}'.format(self.username, new_password)
                            self.send_message(s, msg)
                            self.receive_message_from_server(s, print_it=True)
                        else:
                            print('   passwords did\'nt match, try again'.upper())

                    # delete user
                    elif option == 7:
                        if input('are you sure? (enter 1 to continue)'.upper()) == '1':
                            msg = 'delete-user {}'.format(self.username)
                            self.send_message(s, msg)
                            self.receive_message_from_server(s, print_it=True)
                            s.close()
                            break  # end of program
                    # cls()
                except ValueError:
                    print(Fore.RED, 'bad input! try again', Fore.WHITE)


if __name__ == '__main__':
    c = Client()
    c.main()

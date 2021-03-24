import socket
import csv

if __name__ == '__main__':
    while True:
        print('-----------------------------')
        print('Select an Option\n 1 - Enter a Hostname\n 2 - Import from CSV file\n-1 - Exit')
        try:
            user_input = int(input())
            if user_input == 1:
                hostname = input(">>> Enter a Hostname: ")
                DNS_record = socket.gethostbyname(hostname)
                print("   >>> A record: {}".format(DNS_record))

            elif user_input == 2:
                pass
            elif user_input == -1:
                break
            else:
                print('Wrong input! Try again.')
        except ValueError:
            print('Wrong input! Try again.')

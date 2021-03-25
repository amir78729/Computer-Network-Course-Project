import socket
import csv
import pandas


def write_on_csv(file_name):
    with open(file_name, mode='w', newline="") as output_file:
        csv_writer = csv.writer(output_file, delimiter=',')
        csv_writer.writerow(['hostname', 'IP Address'])
        for d in data:
            if any(d):
                csv_writer.writerow(d)


if __name__ == '__main__':
    while True:
        print('-----------------------------')
        print("Select an Option\n"
              " 1 - Enter a Hostname\n"
              " 2 - Import from CSV file\n"
              "-1 - Exit")
        try:
            user_input = int(input())
            # entering a hostname
            if user_input == 1:
                hostname = input(">>> Enter a Hostname: ")
                DNS_record = socket.gethostbyname(hostname)
                print("   >>> A record: {}".format(DNS_record))

            # importing from a csv file
            elif user_input == 2:

                # counting lines
                with open('Q3_csv_input.csv') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    lines = len(list(csv_reader)) - 1

                # reading from Q3_csv_input.csv
                with open('Q3_csv_input.csv') as csv_file:
                    print('>>> Reading from \"Q3_csv_input.csv\"')
                    data = []
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    # lines = len(list(csv_reader))
                    line_count = 0
                    for row in csv_reader:

                        try:
                            row_list = []
                            if line_count == 0:
                                # print(f'Column names are {", ".join(row)}')
                                line_count += 1
                            else:
                                hostname = row[0]
                                print('   >>> ({}/{}) : {} '.format(line_count, lines, hostname))
                                row_list.append(hostname)
                                host_info = socket.gethostbyaddr(hostname)
                                # print(A_record)

                                row_list.append(host_info[2][0])
                                line_count += 1
                                data.append(row_list)
                        except IndexError:
                            line_count += 1
                        except socket.herror:
                            # print('Host not found')
                            row_list.append(socket.gethostbyname(hostname))
                            data.append(row_list)
                            line_count += 1
                    print()
                # writing to Q3_csv_output.csv
                write_on_csv('Q3_csv_output.csv')

                # printing the output
                print('>>> Output')
                print(pandas.read_csv('Q3_csv_output.csv'))

            # end of program
            elif user_input == -1:
                break
            else:
                print('Something went wrong! Try again.')
        except (socket.gaierror, ValueError):
            print('Something went wrong! Try again.')

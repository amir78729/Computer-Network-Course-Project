import socket
import csv
import pandas

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
                # reading from Q3_csv_input.csv
                with open('Q3_csv_input.csv') as csv_file:
                    data = []
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    line_count = 0
                    for row in csv_reader:
                        row_list = []
                        if line_count == 0:
                            # print(f'Column names are {", ".join(row)}')
                            line_count += 1
                        else:
                            hostname = row[0]
                            A_record = socket.gethostbyname(hostname)

                            row_list.append(hostname)
                            row_list.append(A_record)
                            line_count += 1
                            data.append(row_list)

                # writing to Q3_csv_output.csv
                with open('Q3_csv_output.csv', mode='w', newline="") as output_file:
                    csv_writer = csv.writer(output_file, delimiter=',')
                    csv_writer.writerow(['hostname', 'A record'])
                    for d in data:
                        if any(d):
                            csv_writer.writerow(d)

                # printing the output
                print(pandas.read_csv('Q3_csv_output.csv'))

            # end of program
            elif user_input == -1:
                break
            else:
                print('Wrong input! Try again.')
        except (socket.gaierror, ValueError):
            print('Wrong input! Try again.')

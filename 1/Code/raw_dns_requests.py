from iterative import *
from caching import *
from collections import OrderedDict
import csv
import pandas


# See https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
# See https://tools.ietf.org/html/rfc1035


def send_udp_message(message, address, port):
    """send_udp_message sends a message to UDP server
    message should be a hexadecimal encoded string
    """
    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), (address, port))
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")


def build_message(type="A", address="", r=1):
    ID = 43690  # 16-bit identifier (0-65535) # 43690 equals 'aaaa'

    QR     = 0  # Query: 0, Response: 1     1bit
    OPCODE = 0  # Standard query            4bit
    AA     = 0  # ?                         1bit
    TC     = 0  # Message is truncated?     1bit
    RD     = r  # RECURSION?                1bit
    RA     = 0  # ?                         1bit
    Z      = 0  # ?                         3bit
    RCODE  = 0  # ?                         4bit

    query_params = str(QR)
    query_params += str(OPCODE).zfill(4)
    query_params += str(AA) + str(TC) + str(RD) + str(RA)
    query_params += str(Z).zfill(3)
    query_params += str(RCODE).zfill(4)
    query_params = "{:04x}".format(int(query_params, 2))

    QDCOUNT = 1  # Number of questions           4bit
    ANCOUNT = 0  # Number of answers             4bit
    NSCOUNT = 0  # Number of authority records   4bit
    ARCOUNT = 0  # Number of additional records  4bit

    message = ""
    message += "{:04x}".format(ID)
    message += query_params
    message += "{:04x}".format(QDCOUNT)
    message += "{:04x}".format(ANCOUNT)
    message += "{:04x}".format(NSCOUNT)
    message += "{:04x}".format(ARCOUNT)

    # QNAME is url split up by '.', preceded by int indicating length of part
    addr_parts = address.split(".")
    for part in addr_parts:
        addr_len = "{:02x}".format(len(part))
        addr_part = binascii.hexlify(part.encode())
        message += addr_len
        message += addr_part.decode()

    message += "00"  # Terminating bit for QNAME

    # Type of request
    QTYPE = get_type(type)
    message += QTYPE

    # Class for lookup. 1 is Internet
    QCLASS = 1
    message += "{:04x}".format(QCLASS)

    return message


def decode_message(message):
    """                                 1  1  1  1  1  1
          0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                      ID                       |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                    QDCOUNT                    |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                    ANCOUNT                    |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                    NSCOUNT                    |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                    ARCOUNT                    |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    ID              A 16 bit identifier assigned by the program that
                    generates any kind of query.  This identifier is copied
                    the corresponding reply and can be used by the requester
                    to match up replies to outstanding queries.

    QR              A one bit field that specifies whether this message is a
                    query (0), or a response (1).

    OPCODE          A four bit field that specifies kind of query in this
                    message.  This value is set by the originator of a query
                    and copied into the response.  The values are:

                    0               a standard query (QUERY)

                    1               an inverse query (IQUERY)

                    2               a server status request (STATUS)

                    3-15            reserved for future use

    AA              Authoritative Answer - this bit is valid in responses,
                    and specifies that the responding name server is an
                    authority for the domain name in question section.

                    Note that the contents of the answer section may have
                    multiple owner names because of aliases.  The AA bit
                    corresponds to the name which matches the query name, or
                    the first owner name in the answer section.

    TC              TrunCation - specifies that this message was truncated
                    due to length greater than that permitted on the
                    transmission channel.

    RD              Recursion Desired - this bit may be set in a query and
                    is copied into the response.  If RD is set, it directs
                    the name server to pursue the query recursively.
                    Recursive query support is optional.

    RA              Recursion Available - this be is set or cleared in a
                    response, and denotes whether recursive query support is
                    available in the name server.

    Z               Reserved for future use.  Must be zero in all queries
                    and responses.

    RCODE           Response code - this 4 bit field is set as part of
                    responses.  The values have the following
                    interpretation:

                    0               No error condition

                    1               Format error - The name server was
                                    unable to interpret the query.

                    2               Server failure - The name server was
                                    unable to process this query due to a
                                    problem with the name server.

                    3               Name Error - Meaningful only for
                                    responses from an authoritative name
                                    server, this code signifies that the
                                    domain name referenced in the query does
                                    not exist.

                    4               Not Implemented - The name server does
                                    not support the requested kind of query.

                    5               Refused - The name server refuses to
                                    perform the specified operation for
                                    policy reasons.  For example, a name
                                    server may not wish to provide the
                                    information to the particular requester,
                                    or a name server may not wish to perform
                                    a particular operation (e.g., zone
                                    transfer) for particular data.

                    6-15            Reserved for future use.

    QDCOUNT         an unsigned 16 bit integer specifying the number of
                    entries in the question section.

    ANCOUNT         an unsigned 16 bit integer specifying the number of
                    resource records in the answer section.

    NSCOUNT         an unsigned 16 bit integer specifying the number of name
                    server resource records in the authority records
                    section.

    ARCOUNT         an unsigned 16 bit integer specifying the number of
                    resource records in the additional records section.

    --------------------------------------------------------------------------

                                        1  1  1  1  1  1
          0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                                               |
        /                     QNAME                     /
        /                                               /
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                     QTYPE                     |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                     QCLASS                    |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    QNAME           a domain name represented as a sequence of labels, where
                    each label consists of a length octet followed by that
                    number of octets.  The domain name terminates with the
                    zero length octet for the null label of the root.  Note
                    that this field may be an odd number of octets; no
                    padding is used.

    QTYPE           a two octet code which specifies the type of the query.
                    The values for this field include all codes valid for a
                    TYPE field, together with some more general codes which
                    can match more than one type of RR.

    QCLASS          a two octet code that specifies the class of the query.
                    For example, the QCLASS field is IN for the Internet.

    --------------------------------------------------------------------------

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                                               |
    /                                               /
    /                      NAME                     /
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TYPE                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     CLASS                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TTL                      |
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                   RDLENGTH                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
    /                     RDATA                     /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    NAME            a domain name to which this resource record pertains.

    TYPE            two octets containing one of the RR type codes.  This
                    field specifies the meaning of the data in the RDATA
                    field.

    CLASS           two octets which specify the class of the data in the
                    RDATA field.

    TTL             a 32 bit unsigned integer that specifies the time
                    interval (in seconds) that the resource record may be
                    cached before it should be discarded.  Zero values are
                    interpreted to mean that the RR can only be used for the
                    transaction in progress, and should not be cached.

    RDLENGTH        an unsigned 16 bit integer that specifies the length in
                    octets of the RDATA field.

    RDATA           a variable length string of octets that describes the
                    resource.  The format of this information varies
                    according to the TYPE and CLASS of the resource record.
                    For example, the if the TYPE is A and the CLASS is IN,
                    the RDATA field is a 4 octet ARPA Internet address.

    :param message:
    :return:
    """
    res = []
    dic = {}
    dic.update({"ID": "???"})
    dic.update({"QNAME": "???"})
    dic.update({"QTYPE": "???"})
    dic.update({"QCLASS": "???"})
    dic.update({"QDCOUNT": "???"})
    dic.update({"ANCOUNT": "???"})
    dic.update({"NSCOUNT": "???"})
    dic.update({"ARCOUNT": "???"})
    dic.update({"ANAME": "???"})
    dic.update({"ATYPE": "???"})
    dic.update({"ACLASS": "???"})
    dic.update({"TTL": "???"})
    dic.update({"RDLENGTH": "???"})
    dic.update({"RDDATA": "???"})
    dic.update({"RDDATA_decoded": "???"})
    # Header
    ID = message[0:4]
    query_params = message[4:8]
    QDCOUNT = message[8:12]
    ANCOUNT = message[12:16]
    NSCOUNT = message[16:20]
    ARCOUNT = message[20:24]

    params = "{:b}".format(int(query_params, 16)).zfill(16)
    QPARAMS = OrderedDict([
        ("QR     ", params[0:1]),
        ("OPCODE ", params[1:5]),
        ("AA     ", params[5:6]),
        ("TC     ", params[6:7]),
        ("RD     ", params[7:8]),
        ("RA     ", params[8:9]),
        ("Z      ", params[9:12]),
        ("RCODE  ", params[12:16])
    ])

    # Question section
    QUESTION_SECTION_STARTS = 24
    question_parts = parse_parts(message, QUESTION_SECTION_STARTS, [])
    try:
        QNAME = ".".join(map(lambda p: binascii.unhexlify(p).decode(), question_parts))
        QTYPE_STARTS = QUESTION_SECTION_STARTS + (len("".join(question_parts))) + (len(question_parts) * 2) + 2
        QCLASS_STARTS = QTYPE_STARTS + 4
        QTYPE = message[QTYPE_STARTS:QCLASS_STARTS]
        QCLASS = message[QCLASS_STARTS:QCLASS_STARTS + 4]
    except:
        pass

    res.append("\n HEADER")
    try:
        dic.update({"ID": ID})
        res.append("    ID: " + ID)
        res.append("    QUERYPARAMS: ")
        for qp in QPARAMS:
            res.append("       " + qp + " : " + QPARAMS[qp])
            dic.update({qp: QPARAMS[qp]})
    except:
        pass
    res.append("\n QUESTION SECTION")
    res.append("    QNAME  : " + QNAME)
    res.append("    QTYPE  : " + QTYPE)
    res.append("    QCLASS : " + QCLASS)
    dic.update({"QNAME": QNAME})
    dic.update({"QTYPE": QTYPE})
    dic.update({"QCLASS": QCLASS})

    # Answer section
    ANSWER_SECTION_STARTS = QCLASS_STARTS + 4

    NUM_ANSWERS = max([int(ANCOUNT, 16), int(NSCOUNT, 16), int(ARCOUNT, 16)])

    if recursion == 1:  # for recursive
        if NUM_ANSWERS > 0:
            res.append("\n ANSWER SECTION")
            for ANSWER_COUNT in range(NUM_ANSWERS):
                if ANSWER_SECTION_STARTS < len(message):
                    ANAME = message[ANSWER_SECTION_STARTS:ANSWER_SECTION_STARTS + 4]  # Refers to Question
                    ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]
                    ACLASS = message[ANSWER_SECTION_STARTS + 8:ANSWER_SECTION_STARTS + 12]
                    TTL = int(message[ANSWER_SECTION_STARTS + 12:ANSWER_SECTION_STARTS + 20], 16)
                    RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                    RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]
                    if ATYPE == get_type("A"):
                        octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]
                        RDDATA_decoded = ".".join(list(map(lambda x: str(int(x, 16)), octets)))
                    else:
                        RDDATA_decoded = ".".join(
                            map(lambda p: binascii.unhexlify(p).decode('iso8859-1'), parse_parts(RDDATA, 0, [])))
                    ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)
                try:
                    ATYPE
                except NameError:
                    None
                else:
                    res.append("    ANSWER #" + str(ANSWER_COUNT + 1))
                    res.append("       QDCOUNT  : " + str(int(QDCOUNT, 16)))
                    res.append("       ANCOUNT  : " + str(int(ANCOUNT, 16)))
                    res.append("       NSCOUNT  : " + str(int(NSCOUNT, 16)))
                    res.append("       ARCOUNT  : " + str(int(ARCOUNT, 16)))
                    res.append("       ANAME    : " + ANAME)
                    # res.append("       ATYPE    : " + ATYPE + " (\"" + get_type(int(ATYPE, 16)) + "\")")
                    res.append("       ATYPE    : " + ATYPE)
                    res.append("       ACLASS   : " + ACLASS)
                    res.append("       TTL      : " + str(TTL))
                    res.append("       RDLENGTH : " + str(RDLENGTH))
                    res.append("       RDDATA   : " + RDDATA + " ( " + RDDATA_decoded + " )\n")
                    dic.update({"QDCOUNT": QDCOUNT})
                    dic.update({"ANCOUNT": ANCOUNT})
                    dic.update({"NSCOUNT": NSCOUNT})
                    dic.update({"ARCOUNT": ARCOUNT})
                    dic.update({"ANAME": ANAME})
                    dic.update({"ATYPE": ATYPE})
                    dic.update({"ACLASS": ACLASS})
                    dic.update({"TTL": TTL})
                    dic.update({"RDLENGTH": RDLENGTH})
                    dic.update({"RDDATA": RDDATA})
                    dic.update({"RDDATA_decoded": RDDATA_decoded})
        return "\n".join(res), dic
    else:  # iterative
        other_servers = []
        answer_found = False
        if NUM_ANSWERS > 0:
            print("\n# ANSWER PART :")

            if int(ANCOUNT, 16) > 0:
                answer_found = True
                print("ANCOUNT==>")
                print("ooohhh Answer Hereeee!!")
                for answer in range(int(ANCOUNT, 16)):
                    if ANSWER_SECTION_STARTS < len(message):

                        ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]

                        RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                        RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]

                        if ATYPE == get_type("A"):
                            octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]

                            ip = ""
                            for x in octets:
                                ip += str(int(x, 16))
                                if octets.index(x) != len(octets) - 1:
                                    ip += '.'
                            RDDATA_decoded = ip

                        else:
                            string = ""
                            arr = parse_parts(RDDATA, 0, [])
                            for x in arr:

                                string += binascii.unhexlify(x).decode('iso8859-1')

                                if (arr.index(x) != len(arr) - 1):
                                    string += '.'
                            RDDATA_decoded = string
                        ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)

                    try:
                        ATYPE
                    except NameError:
                        None
                    else:

                        print(" ANSWER Part : " + str(answer + 1))

                        print("RDDATA decoded: " + RDDATA_decoded + "\n")

            if int(NSCOUNT, 16) > 0:
                print("NSCOUNT==>")
                for answer in range(int(NSCOUNT, 16)):
                    if ANSWER_SECTION_STARTS < len(message):

                        ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]

                        RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                        RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]

                        if ATYPE == get_type("A"):
                            octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]

                            ip = ""
                            for x in octets:
                                ip += str(int(x, 16))
                                if (octets.index(x) != len(octets) - 1):
                                    ip += '.'
                            RDDATA_decoded = ip

                        else:
                            string = ""
                            arr = parse_parts(RDDATA, 0, [])
                            for x in arr:

                                string += binascii.unhexlify(x).decode('iso8859-1')

                                if (arr.index(x) != len(arr) - 1):
                                    string += '.'
                            RDDATA_decoded = string
                        ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)

                    try:
                        ATYPE
                    except NameError:
                        None
                    else:
                        print(" ANSWER Part " + str(answer + 1))

                        print("RDDATA decoded : " + RDDATA_decoded + "\n")

            if int(ARCOUNT, 16) > 0:
                print("ARCOUNT==>")

                for answer in range(int(ARCOUNT, 16)):
                    if (ANSWER_SECTION_STARTS < len(message)):
                        ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]
                        typ = get_type(int(ATYPE, 16))

                        RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                        RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]

                    if ATYPE == get_type("A"):
                        octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]

                        ip = ""
                        for x in octets:
                            ip += str(int(x, 16))
                            if (octets.index(x) != len(octets) - 1):
                                ip += '.'
                        RDDATA_decoded = ip

                    else:
                        string = ""
                        arr = parse_parts(RDDATA, 0, [])
                        for x in arr:

                            string += binascii.unhexlify(x).decode('iso8859-1')

                            if (arr.index(x) != len(arr) - 1):
                                string += '.'
                        RDDATA_decoded = string
                    ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)
                    if typ == 'A':
                        print("hereee")

                        other_servers.append(RDDATA_decoded)

                    try:
                        ATYPE
                    except NameError:
                        None
                    else:
                        print(" ANSWER Part : " + str(answer + 1))

                        print("RDDATA decoded : " + RDDATA_decoded + "\n")

        return "\n".join(res), dic, other_servers, answer_found


def get_type(type):
    types = ["ERROR", "A", "NS", "MD", "MF", "CNAME", "SOA", "MB", "MG", "MR", "NULL", "WKS", "PTS", "HINFO", "MINFO",
             "MX", "TXT"]
    if type == 28:
        return "AAAA"
    return "{:04x}".format(types.index(type)) if isinstance(type, str) else types[type]


def parse_parts(msg, start, parts):
    part_start = start + 2
    part_len = msg[start:part_start]
    if len(part_len) == 0:
        return parts
    part_end = part_start + (int(part_len, 16) * 2)
    parts.append(msg[part_start:part_end])

    if msg[part_end:part_end + 2] == "00" or part_end > len(message):
        return parts
    else:
        return parse_parts(msg, part_end, parts)


def print_message(msg):
    n = 4
    split_strings = [msg[index: index + n] for index in range(0, len(msg), n)]
    for line in split_strings:
        print("   {} ({})".format(" ".join(bin(int(line, 16))[2:].zfill(16)), line))


if __name__ == '__main__':
    count = {}  # used in caching

    database = "cache.sql"
    conn = create_connection(database)

    dns_cache_table = """ CREATE TABLE IF NOT EXISTS dns_cache (
                                            HOSTNAME_RECORD_RECURSION text PRIMARY KEY,
                                            RESPONSE text
                                        ); """

    if conn is not None:
        # create projects table
        create_table(conn, dns_cache_table)

    else:
        print("Error... Caching is NOT active!.")

    while True:
        print('-'*100)
        print("Select an Option\n"
              " 1 - Enter a Hostname\n"
              " 2 - Import from CSV File\n"
              " 3 - See Cache Data\n"
              " 4 - Clear Cache\n"
              "-1 - Exit")
        try:
            user_input = int(input())
            # entering a hostname
            if user_input == 1:
                url = input(">>> Enter a URL: ")
                record = input(">>> Enter a Record Type: ").upper()
                while True:
                    recursion = int(input(">>> Recursive Queries(1) or Iterative Queries?(0)"))
                    if recursion == 1 or recursion == 0:
                        break
                    else:
                        print('   >>> You Have to enter 0 or 1! Try again...')
                cache_string = url + '_' + record + '_' + str(recursion)
                if check_if_exists(conn, cache_string):
                    print('\n*** Data is in the cache!')
                    if recursion == 1:
                        response = get_response_from_cache(conn, cache_string)[0][0]
                        # print("\nResponse:")
                        # print_message(response)
                        print("\tRestored Data From cache: " + response)
                    else:
                        response = get_response_from_cache(conn, cache_string)[0][0]
                        # print("\nResponse:")
                        # print_message(response)
                        print("\tRestored Data From cache: " + response)
                else:
                    print('\n*** Data is not in the cache!')
                    # if this is the 1st time that user has entered this request...
                    if cache_string not in count.keys():
                        count[cache_string] = 1
                    # if the user has requested this before...
                    else:
                        count.update({cache_string: count[cache_string] + 1})

                    if recursion == 1:
                        message = build_message(record, url, recursion)
                        print("Request:")
                        print_message(message)
                        print("\nRequest (decoded):" + decode_message(message)[0])

                        # second argument is external DNS server, third argument is port
                        response = send_udp_message(message, "1.1.1.1", 53)
                        print("\nResponse:")
                        print_message(response)
                        print("\nResponse (decoded):" + decode_message(response)[0])
                        response = decode_message(response)[1]['RDDATA_decoded']
                    else:
                        response = find_iterative(url)
                        response = str(response).split(' ')[-1]
                        print('\tanswer: {}'.format(response))

                    if count[cache_string] == 3:
                        print('*** ADDING THIS REQUEST TO THE CACHE!')
                        add_new_data(conn, (cache_string, response))

            # importing from a csv file
            elif user_input == 2:
                recursion = 1
                records = ['HOSTNAME', 'A', 'SOA']
                # counting lines
                with open('csv_input.csv') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    lines = len(list(csv_reader)) - 1

                # reading from csv_input.csv
                with open('csv_input.csv') as csv_file:
                    print('>>> Reading from \"csv_input.csv\"')
                    data = []
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    # lines = len(list(csv_reader))
                    line_count = 0
                    for row in csv_reader:
                        try:
                            row_list = []
                            if line_count == 0:
                                line_count += 1
                            else:
                                hostname = row[0]
                                print('   >>> ({}/{}) : {} '.format(line_count, lines, hostname), end="")
                                row_list.append(hostname)
                                for r in records:
                                    if r != 'HOSTNAME':
                                        print("\t", r, end=': ')
                                        try:
                                            message = build_message(r, hostname, recursion)
                                            # second argument is external DNS server, third argument is port
                                            response = send_udp_message(message, "1.1.1.1", 53)
                                            row_list.append(decode_message(response)[1].get("RDDATA_decoded"))
                                            if decode_message(response)[1].get("RDDATA_decoded") != '???':
                                                print('DONE  ', end='\t')
                                            else :
                                                print('FAILED', end='\t')
                                        except:
                                            row_list.append("???")
                                            print('FAILED', end='\t')
                                            pass
                                line_count += 1
                                data.append(row_list)
                                print()
                        except IndexError:
                            line_count += 1
                        except socket.herror:
                            row_list.append(socket.gethostbyname(hostname))
                            data.append(row_list)
                            line_count += 1
                    print()

                # writing to csv_output.csv
                with open('csv_output.csv', mode='w', newline="", encoding="utf-8") as output_file:
                    csv_writer = csv.writer(output_file, delimiter=',')
                    csv_writer.writerow(records)
                    for d in data:
                        if any(d):
                            csv_writer.writerow(d)

                # printing the output
                print('>>> Output')
                df = pandas.read_csv('csv_output.csv', index_col="HOSTNAME")
                print(df)
                df.head(10)
                df.describe()
                print('\nNOTE: Complete data can be seen in the CSV file, also in the CSV file there is only one of the'
                      '\nanswers, To see all of them you can choose the 1st option in the main menu.\n')

            # end of program
            elif user_input == -1:
                break

            # see cache
            elif user_input == 3:
                cache_data = get_cache(conn)
                if len(cache_data) != 0:
                    i = 1
                    for data in cache_data:
                        d_hostname, d_record, d_recursion_bit = data[0].split('_')

                        if d_recursion_bit == 0:
                            d_recursion = 'iterative'
                        else:
                            d_recursion = 'recursive'
                        print('{})\t{} ({} record with RD={}) :\n\t{}\n\t\n'.format(i, d_hostname, d_record,
                                                                                    d_recursion_bit, data[1]
                                                                                    ))
                        i += 1
                else:
                    print('The Cache is Empty')

            # clear cache
            elif user_input == 4:
                if input('Are you Sure?\nType \"Y\" to continue: ').upper() == 'Y':
                    clear_cache(conn)
                    print('*** The Cache is Empty')
                else:
                    print(' canceled...')

            # bad input
            else:
                print('Something went wrong! Try again.')
        except (socket.gaierror, ValueError):
            print('Something went wrong! Try again.')

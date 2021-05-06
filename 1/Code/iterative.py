import binascii
import socket
import dnslib

Qname_size = 0


def print_message(msg):
    n = 4
    split_strings = [msg[index: index + n] for index in range(0, len(msg), n)]
    for line in split_strings:
        print("   {} ({})".format(" ".join(bin(int(line, 16))[2:].zfill(16)), line))


def send_query(message, address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.sendto(binascii.unhexlify(message), (address, port))

    data, _ = sock.recvfrom(4096)

    sock.close()
    return binascii.hexlify(data).decode("utf-8")


def build_message(type, address):
    ID = 14579
    message = ""
    message += "{:04x}".format(ID)

    QR = 0  # Query: 0, Response: 1  1bit
    OPCODE = 0  # Standard query    4bit
    AA = 0  # Authoritative Answer 1bit
    TC = 0  # truncated 1bit
    RD = 0  # Recursion 1bit
    RA = 0  # Recursion Available  1bit
    Z = 0  # zero 3bit

    RCODE = 0  # Response code 4bit

    flags = str(QR)
    flags += str(OPCODE).zfill(4)
    flags += str(AA) + str(TC) + str(RD) + str(RA)
    flags += str(Z).zfill(3)
    flags += str(RCODE).zfill(4)
    flags = "{:04x}".format(int(flags, 2))

    QDCOUNT = 1  # Number of questions           4bit
    ANCOUNT = 0  # Number of answers             4bit
    NSCOUNT = 0  # Number of authority records   4bit
    ARCOUNT = 0  # Number of additional records  4bit

    message += flags
    message += "{:04x}".format(QDCOUNT)
    message += "{:04x}".format(ANCOUNT)
    message += "{:04x}".format(NSCOUNT)
    message += "{:04x}".format(ARCOUNT)

    addrsSplit = address.split(".")
    qnameSize = 0
    global Qname_size
    for part in addrsSplit:
        byteTosned = "{:02x}".format(len(part))

        host_part = binascii.hexlify(part.encode())
        message += byteTosned
        message += host_part.decode()
        qnameSize += len(byteTosned)
        qnameSize += len(host_part.decode())

    Qname_size = qnameSize

    message += "00"

    QTYPE = get_type(type)
    message += QTYPE

    QCLASS = 1
    message += "{:04x}".format(QCLASS)

    return message


def decode_message(message):
    other_servers = []
    answer_found = False
    ANCOUNT = message[12:16]
    print('\tANCount: ' + ANCOUNT)
    NSCOUNT = message[16:20]
    print('\tNSCount: ' + NSCOUNT)
    ARCOUNT = message[20:24]
    print('\tARCount: ' + ARCOUNT)
    qname_end = 24 + Qname_size + 2
    Qtype_start = qname_end
    Qclass_start = Qtype_start + 4
    # Answer section
    answer_start = Qclass_start + 4
    typ = ""
    answer_num = max([int(ANCOUNT, 16), int(NSCOUNT, 16), int(ARCOUNT, 16)])
    if answer_num > 0:
        print("\n# ANSWER PART :")
        if int(ANCOUNT, 16) > 0:
            answer_found = True
            print("ANCOUNT:")
            for answer in range(int(ANCOUNT, 16)):
                if (answer_start < len(message)):
                    ATYPE = message[answer_start + 4:answer_start + 8]
                    RDLENGTH = int(message[answer_start + 20:answer_start + 24], 16)
                    RDDATA = message[answer_start + 24:answer_start + 24 + (RDLENGTH * 2)]
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
                        arr = splitting(RDDATA, 0, [])
                        for x in arr:
                            string += binascii.unhexlify(x).decode('iso8859-1')
                            if (arr.index(x) != len(arr) - 1):
                                string += '.'
                        RDDATA_decoded = string
                    answer_start = answer_start + 24 + (RDLENGTH * 2)
                try:
                    ATYPE
                except NameError:
                    pass
                else:
                    print("\tANSWER Part : " + str(answer + 1))
                    print("\t\tRDDATA decoded: " + RDDATA_decoded + "\n")
        if int(NSCOUNT, 16) > 0:
            print("NSCOUNT:")
            for answer in range(int(NSCOUNT, 16)):
                if answer_start < len(message):
                    ATYPE = message[answer_start + 4:answer_start + 8]
                    RDLENGTH = int(message[answer_start + 20:answer_start + 24], 16)
                    RDDATA = message[answer_start + 24:answer_start + 24 + (RDLENGTH * 2)]
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
                        arr = splitting(RDDATA, 0, [])
                        for x in arr:
                            string += binascii.unhexlify(x).decode('iso8859-1')
                            if arr.index(x) != len(arr) - 1:
                                string += '.'
                        RDDATA_decoded = string
                    answer_start = answer_start + 24 + (RDLENGTH * 2)
                try:
                    ATYPE
                except NameError:
                    None
                else:
                    print("\tANSWER Part " + str(answer + 1))
                    print("\t\tRDDATA decoded : " + RDDATA_decoded + "\n")
        if int(ARCOUNT, 16) > 0:
            print("ARCOUNT:")
            for answer in range(int(ARCOUNT, 16)):
                if answer_start < len(message):
                    ATYPE = message[answer_start + 4:answer_start + 8]
                    typ = get_type(int(ATYPE, 16))
                    RDLENGTH = int(message[answer_start + 20:answer_start + 24], 16)
                    RDDATA = message[answer_start + 24:answer_start + 24 + (RDLENGTH * 2)]
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
                    arr = splitting(RDDATA, 0, [])
                    for x in arr:
                        string += binascii.unhexlify(x).decode('iso8859-1')
                        if (arr.index(x) != len(arr) - 1):
                            string += '.'
                    RDDATA_decoded = string
                answer_start = answer_start + 24 + (RDLENGTH * 2)
                if typ == 'A':
                    other_servers.append(RDDATA_decoded)
                try:
                    ATYPE
                except NameError:
                    None
                else:
                    print("\tANSWER Part : " + str(answer + 1))
                    print("\t\tRDDATA decoded : " + RDDATA_decoded + "\n")
    return other_servers, answer_found


def get_type(type):
    types = [
        "ERROR",  # type 0 does not exist
        "A",
        "NS",
        "MD",
        "MF",
        "CNAME",
        "SOA",
        "MB",
        "MG",
        "MR",
        "NULL",
        "WKS",
        "PTS",
        "HINFO",
        "MINFO",
        "MX",
        "TXT"
    ]
    if type == 28:
        return "AAAA"
    else:
        return "{:04x}".format(types.index(type)) if isinstance(type, str) else types[type]


def splitting(message, start, parts):
    start_part = start + 2
    part_size = message[start:start_part]
    if len(part_size) == 0:
        return parts
    end_part = start_part + (int(part_size, 16) * 2)
    parts.append(message[start_part:end_part])
    if message[end_part:end_part + 2] == "00" or end_part > len(message):
        return parts
    else:
        return splitting(message, end_part, parts)


def find_iterative(url):
    message = build_message("A", url)
    print("Request:\n")
    print_message(message)
    print("\nRequest (decoded):")
    decode_message(message)
    flag = True
    response = send_query(message, "198.41.0.4", 53)
    print("\nResponse:\n")
    print_message(response)
    print("\nResponse (decoded):")
    servers, f = decode_message(response)
    if f:  # answer found (ANCOUNT > 0)
        return
    for server in servers:
        print(server)
    while flag:
        print("Trying with {}".format(servers[0]))
        response = send_query(message, servers[0], 53)
        print("\nResponse:\n")
        print_message(response)
        print("\nResponse (decoded):")
        x, d = decode_message(response)
        if d:
            packet = binascii.unhexlify(response)
            d = dnslib.DNSRecord.parse(packet)
            print('THE ANSWER IS READY!')
            return d
        else:
            if not len(x) == 0:
                servers = x
                # print(x)
                for j in x:
                    print('\t{}'.format(j))
            else:
                nss = []
                packet = binascii.unhexlify(response)
                d = dnslib.DNSRecord.parse(packet)
                arr = str(d).split("\n")
                for i in arr:
                    if "IN      NS" in i:
                        # print(i)
                        s = str(i).split(" ")
                        nss.append(s[len(s) - 1])
                        for j in nss:
                            print("\tTrying with {}".format(j))
                            response = send_query(message, str(j), 53)
                            print("\nResponse:\n" )
                            print_message(response)
                            print("\nResponse (decoded):")
                            x, d = decode_message(response)
                            # print(x)
                            if d:
                                packet = binascii.unhexlify(response)
                                d = dnslib.DNSRecord.parse(packet)
                                # print(d)
                                print('THE ANSWER IS READY!')
                                return d

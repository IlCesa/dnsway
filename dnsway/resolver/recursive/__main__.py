from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.dns_message import DnsMessage
import socket


'''




'''



import sys

# endianness = sys.byteorder
# print(f"L'endianness del sistema è: {endianness}")

dns_message = DnsMessage()
dns_message.header.set_query_type(query_type=QUERY_TYPE.QUERY)
dns_message.header.set_opcode(opcode_type=OPCODE_TYPE.QUERY)
dns_message.header.set_aa(False)
dns_message.header.set_tc(False)
dns_message.header.set_rd(True)
dns_message.header.set_ra(True)
dns_message.header.qdcount = 1
dns_message.header.ancount = 0
dns_message.header.nscount = 0
dns_message.header.arcount = 0


dns_message.question.qname  = "www.google.com"
dns_message.question.qtype  = QTYPE_VALUES.AAAA
dns_message.question.qclass = QCLASS_VALUES.IN

dns_message.hex_dump()

encoded_dns_message = dns_message.encode()

server_address = ("8.8.8.8", 53)
msg_byte_length = len(encoded_dns_message)
print(dns_message.question.length())
print(f"byte size: {msg_byte_length}. encoded message: {encoded_dns_message}")
print(dns_message.length())
if msg_byte_length <= 512:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        print(f"Sending DNS query using UDP -> {server_address[0]}:{server_address[1]}...")
        sock.sendto(dns_message.encode(), server_address)
        data, addr = sock.recvfrom(4096)
        print(f"Ricevuto {len(data)} byte da {addr}")
        print(f"Contenuto: {data}")
        res = DnsMessage()
        res.decode(data)
        res.hex_dump()
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        sock.close()
else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Sending DNS query using TCP -> {server_address[0]}:{server_address[1]}...")
        sock.connect(server_address)
        msg = bytearray()
        msg = msg + msg_byte_length.to_bytes(length=2, byteorder='big') + dns_message.encode()

        sock.sendall(msg)
        response = bytes()
        while True:
            rcvd = sock.recv(4096) 
            print(rcvd)
            response = response + rcvd
            if len(rcvd) == 0:
                break
        print(f"Ricevuto: {response}")
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        sock.close()


import socket
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE


dns_message = DnsMessage()
dns_message.header.set_query_type(query_type=QUERY_TYPE.QUERY)
dns_message.header.set_opcode(opcode_type=OPCODE_TYPE.QUERY)
dns_message.header.set_aa(False)
dns_message.header.set_tc(False)
dns_message.header.set_rd(True)
dns_message.header.set_ra(True)
dns_message.header.qdcount = 1
dns_message.header.ancount = 0
dns_message.header.arcount = 0

dns_message.question.qname = "google.it"
dns_message.question.qtype = QTYPE_VALUES.A
dns_message.question.qclass = QCLASS_VALUES.IN

print(dns_message.encode())

#dns_message.dump_message()

server_address = ("1.1.1.1", 53)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    print(f"Invio della query DNS  tramite UDP a {server_address[0]}:{server_address[1]}...")
    sock.sendto(dns_message.encode(), server_address)

    # Ricevi i dati dal socket
    data, addr = sock.recvfrom(4096)  # Leggi fino a 4096 byte
    print(f"Ricevuto {len(data)} byte da {addr}")
    print(f"Contenuto: {data}")


except Exception as e:
    print(f"Errore: {e}")

finally:
    sock.close()



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    print(f"Invio della query DNS  tramite TCP   a {server_address[0]}:{server_address[1]}...")

    # Connessione al server DNS (porta 53)
    sock.connect(server_address)
    sock.sendall(dns_message.encode())
    # Ricevi i dati dal socket
    respone = sock.recv(4096)  # Leggi fino a 4096 byte
    print(f"Ricevuto: {respone.hex()}")


except Exception as e:
    print(f"Errore: {e}")

finally:
    sock.close()

print("--------------")
print(dns_message.encode())
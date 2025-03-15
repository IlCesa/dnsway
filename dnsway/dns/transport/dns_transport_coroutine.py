from dnsway.dns.message.dns_message import DnsMessage
from abc import abstractmethod
from enum import Enum
import socket


class TRANSPORT_MODE(Enum):
    DATAGRAM            =   0x01      
    VIRTUAL_CIRCUIT     =   0x02              


class DnsWayTransport():
    MAX_UDP_PAYLOAD = 512
    @abstractmethod
    def send(self, dns_message:DnsMessage): ...

    @abstractmethod
    def recv(self): ...


class DnsWayTransportFactory():
    def __init__(self):
        pass
    # NB: per un factory method puro dovremmo fare l'override di un metodo factory da un'interfaccia/classe astratta ma hey, that's python :)
    def create_transport(self, transport_mode: TRANSPORT_MODE, address:str, port:int, timeout:int=5, msg_byte_length:int=0) -> DnsWayTransport:
        dns_transport = None

        if transport_mode == TRANSPORT_MODE.VIRTUAL_CIRCUIT or msg_byte_length > DnsWayTransport.MAX_UDP_PAYLOAD:
            dns_transport = DnsWayTcpTransport(address, port, timeout)
        elif transport_mode == TRANSPORT_MODE.DATAGRAM:
            dns_transport = DnsWayUdpTransport(address, port, timeout)
        return dns_transport


class DnsWayUdpTransport(DnsWayTransport):
    def __init__(self, address:str, port:int, timeout:int=None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.address = address
        self.port = port


    def send(self, dns_message:DnsMessage) -> None:
        self.socket.sendto(dns_message.encode(), (self.address, self.port))


    def recv(self):
        # print("waiting msg response")
        data, addr = self.socket.recvfrom(4096)
        # dns_message = DnsMessage()
        # dns_message.decode(data)
        return DnsMessage.Decode(data)


class DnsWayTcpTransport(DnsWayTransport):
    def __init__(self, address:str, port:int, timeout:int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((address, port))


    def send(self, dns_message:DnsMessage):
        raw_msg_bytearray = dns_message.encode()
        self.socket.sendall(len(raw_msg_bytearray).to_bytes(length=2, byteorder='big') + raw_msg_bytearray)


    def recv(self):
        response = bytes()
        first_byte_rcvd = False
        byte_rcvd = 0
        msg_length = 0
        bufsize = 1024
        while True:
            rcvd = self.socket.recv(bufsize)
            byte_rcvd += bufsize
            if not first_byte_rcvd:
                first_byte_rcvd = True
                msg_length = int.from_bytes(rcvd[:2], byteorder='big')
                rcvd = rcvd[2:]
            byte_to_consume = msg_length % byte_rcvd
            response = response + rcvd[:byte_to_consume]
            if bufsize >= msg_length:
                break
        
        # dns_message = DnsMessage()
        # dns_message.decode(response)
        return DnsMessage.Decode(response)

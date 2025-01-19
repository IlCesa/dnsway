import argparse
import sys

from dnsway.dns.message.dns_message import DnsMessageBuilder
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE
from dnsway.dns.transport.dns_transport import TRANSPORT_MODE, DnsWayTransport, DnsWayTransportFactory, DnsWayUdpTransport

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DNS Query Tool")
    parser.add_argument("domain_name", type=str, help='domain name question')
    parser.add_argument("--qtype", choices=["A", "AAAA", "CNAME"], help="question record qtype",default='A')
    parser.add_argument("--qclass", choices=["IN", "CH"], help="question record qclass", default='IN')
    parser.add_argument("--resolver", type=str, help="recursive resolver address [address]", default='8.8.8.8')
    parser.add_argument("--port", type=int, help="recursive resolver port [port]", default=54)
    args, unk_args = parser.parse_known_args()

    dns_message = (DnsMessageBuilder()
               .set_message_type(query_type=QUERY_TYPE.QUERY)
               .set_opcode(opcode_type=OPCODE_TYPE.QUERY)
               .set_question(domain_name=args.domain_name, qtype=args.qtype, qclass=args.qclass)
               .enable_rd()
               .build())
    
    dns_message.hex_dump()
    dnsway_trasport = DnsWayTransportFactory().create_transport(transport_mode=TRANSPORT_MODE.DATAGRAM,
                                                                address=args.resolver,
                                                                port=args.port)
    # dnsway_trasport = DnsWayUdpTransport(address=args.resolver, port=args.port, timeout=1)
    dnsway_trasport.send(dns_message=dns_message)
    recv_dns_message = dnsway_trasport.recv()
    print(bin(recv_dns_message.header.flags.value).zfill(16))
    recv_dns_message.hex_dump()

    #dns_message.hex_dump()
    ## perform request though dns_transport (setting trasport type etc).
    ## wait response
    ## once response recvd we should: determine if ra is setted in the response
    ## if not, error message indicating that resolver doest accept recursion service.
    ## if yes, check the TC BIT
    ## if it is enabled -> swtich to tcp connection
    ## else iterate through answer RRDATA list and print the informations
    
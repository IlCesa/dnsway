import asyncio

from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.dns.message.utils.dns_message_view import DnsMessageView


class DnsWayUdpResolver():
    HOST = '127.0.0.1'
    PORT = 5353

    async def start(self, asyncio_loop):
        print(f"DnsWay Udp Resolver listening on: {self.HOST}:{self.PORT}")
        transport, protocol = await asyncio_loop.create_datagram_endpoint(lambda: DnsWayUdpResolver(), local_addr=(self.HOST, self.PORT))
        try:
            await asyncio.Future()
        finally:
            transport.close()


    def connection_made(self, transport):
        self.transport = transport


    def datagram_received(self, data, addr):
        address, port = addr
        print(address,port)
        # print(f"Ricevuto pacchetto da {addr}: {data.hex()}")
        # self.transport.sendto(b"ACK", addr)
        print(type(data))

        # simple logic here but this is a direct dependency, we should refactor using dependency injection
        dns_message = DnsMessage()
        dns_message.decode(data)
        dns_message.hex_dump()
        dns_message_view:DnsMessageView = DnsMessageConverter().raw_msg_to_view(dns_message)

        # print(dns_message_view.question.name)



async def main():
    loop = asyncio.get_running_loop()
    await DnsWayUdpResolver().start(loop)


if __name__ == "__main__":
    asyncio.run(main())
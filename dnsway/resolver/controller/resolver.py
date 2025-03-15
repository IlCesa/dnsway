import asyncio

from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.utils.converter import DnsMessageConverter

from dnsway.resolver.service.resolver_service import DnsServerResolverServiceImpl



class DnsWayResolverServer:
    def __init__(self):
        pass

    def start(self):
        asyncio.run(self.__start())

    async def __start(self):
        loop = asyncio.get_running_loop()
        await asyncio.gather(DnsWayUdpResolver.start(loop))


class DnsWayUdpResolver:
    HOST = '127.0.0.1'
    PORT = 5353

    def __init__(self, service_layer):
        self.service_layer = service_layer

    def connection_made(self, transport):
        self.transport = transport


    def datagram_received(self, data, addr):
        # address, port = addr
        # anche qui andrebbe fatto un try catch
        dns_message = DnsMessage.Decode(data)
        dns_message_view = DnsMessageConverter().to_view(dns_message)
        res_msg_view = DnsServerResolverServiceImpl(query_history_of_work=None).process(dns_message_view)
        print(res_msg_view)
        res_dns_msg = DnsMessageConverter().to_msg(res_msg_view)
        self.transport.sendto(res_dns_msg.encode(), addr)


    @staticmethod
    async def start(asyncio_loop):
        print(f"DnsWay Udp Resolver listening on: {DnsWayUdpResolver.HOST}:{DnsWayUdpResolver.PORT}")
        service_layer = None #DnsServerResolverServiceImpl(rootserver_repository=FileRootRepository('dnsway/server/data/root.txt'), cache_unit_of_work=InMemoryRepository())
        transport, protocol = await asyncio_loop.create_datagram_endpoint(lambda: DnsWayUdpResolver(service_layer=service_layer), local_addr=(DnsWayUdpResolver.HOST, DnsWayUdpResolver.PORT))
        try:
            await asyncio.Future()
        finally:
            transport.close()


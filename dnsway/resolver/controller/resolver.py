import asyncio

from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.utils.converter import DnsMessageConverter

from dnsway.dns.message.utils.dns_message_view import DnsMessageView
from dnsway.resolver.service.resolver_service import DnsServerResolverServiceImpl
from dnsway.resolver.service.unit_of_work import QueryHistoryUnitOfWork



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

    def __init__(self, service_layer, query_history_uow):
        self.service_layer = service_layer
        self.qrh_uow = query_history_uow

    def connection_made(self, transport):
        self.transport = transport

    async def process(self, data):
        dns_message = DnsMessage.Decode(data)
        dns_message_view = DnsMessageConverter().to_view(dns_message)
        # print(dns_message_view)
        res_msg_view = await DnsServerResolverServiceImpl(query_history_of_work=self.qrh_uow).process(dns_message_view)
        # print(res_msg_view)
        res_dns_msg = DnsMessageConverter().to_msg(res_msg_view)
        return res_dns_msg
        
    def datagram_received(self, data, addr):
        task = asyncio.create_task(self.process(data))
        task.add_done_callback(lambda future:  self.transport.sendto(future.result().encode(), addr))

    @staticmethod
    async def start(asyncio_loop):
        print(f"DnsWay Udp Resolver listening on: {DnsWayUdpResolver.HOST}:{DnsWayUdpResolver.PORT}")
        service_layer = None #DnsServerResolverServiceImpl(rootserver_repository=FileRootRepository('dnsway/server/data/root.txt'), cache_unit_of_work=InMemoryRepository())
        qrh_uow = QueryHistoryUnitOfWork()
        transport, protocol = await asyncio_loop.create_datagram_endpoint(lambda: DnsWayUdpResolver(service_layer=service_layer, query_history_uow=qrh_uow), local_addr=(DnsWayUdpResolver.HOST, DnsWayUdpResolver.PORT))
        
        try:
            while True:
                await asyncio.sleep(1)
        except:
            transport.close()


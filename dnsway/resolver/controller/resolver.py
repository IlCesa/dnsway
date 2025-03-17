from dnsway.resolver.service.resolver_service import DnsServerResolverServiceImpl
from dnsway.resolver.service.unit_of_work import QueryHistoryUnitOfWork
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.dns.message.dns_message import DnsMessage
import asyncio


class DnsWayResolverServer:
    def start(self):
        asyncio.run(self.__start())

    async def __start(self):
        loop = asyncio.get_running_loop()
        await asyncio.gather(DnsWayUdpResolver.start(loop))


class DnsWayUdpResolver:
    HOST = '127.0.0.1'
    PORT = 5353

    def __init__(self, query_history_uow):
        self.qrh_uow = query_history_uow

    def connection_made(self, transport):
        self.transport = transport

    async def process(self, data):
        dns_message = DnsMessage.Decode(data)
        dns_message_view = DnsMessageConverter().to_view(dns_message)
        res_msg_view = await DnsServerResolverServiceImpl(query_history_of_work=self.qrh_uow).process(dns_message_view)
        res_dns_msg = DnsMessageConverter().to_msg(res_msg_view)
        return res_dns_msg
        
    def datagram_received(self, data, addr):
        task = asyncio.create_task(self.process(data))
        task.add_done_callback(lambda future:  self.transport.sendto(future.result().encode(), addr))

    @staticmethod
    async def start(asyncio_loop):
        print(f"DnsWay Udp Resolver listening on: {DnsWayUdpResolver.HOST}:{DnsWayUdpResolver.PORT}")
        qrh_uow = QueryHistoryUnitOfWork()
        transport, protocol = await asyncio_loop.create_datagram_endpoint(lambda: DnsWayUdpResolver(query_history_uow=qrh_uow), local_addr=(DnsWayUdpResolver.HOST, DnsWayUdpResolver.PORT))
        try:
            while True:
                await asyncio.sleep(1)
        except:
            transport.close()


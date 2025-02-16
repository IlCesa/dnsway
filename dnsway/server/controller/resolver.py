import asyncio

from dnsway.server.adapters.rootserver_repository import FileRootRepository
from dnsway.server.service.service import DnsServerResolverServiceImpl


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
        address, port = addr
        print(address,port)
        print(f"Ricevuto pacchetto da {addr}: {data.hex()}")
        res = self.service_layer.process(data)
        self.transport.sendto(res.encode(), addr)


    @staticmethod
    async def start(asyncio_loop):
        print(f"DnsWay Udp Resolver listening on: {DnsWayUdpResolver.HOST}:{DnsWayUdpResolver.PORT}")
        
        service_layer = DnsServerResolverServiceImpl(rootserver_repository=FileRootRepository('dnsway/server/data/root.txt'))
        transport, protocol = await asyncio_loop.create_datagram_endpoint(lambda: DnsWayUdpResolver(service_layer=service_layer), local_addr=(DnsWayUdpResolver.HOST, DnsWayUdpResolver.PORT))
        try:
            await asyncio.Future()
        finally:
            transport.close()


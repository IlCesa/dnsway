import asyncio


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
        print(f"Ricevuto pacchetto da {addr}: {data.hex()}")
        self.transport.sendto(b"ACK", addr)


async def main():
    loop = asyncio.get_running_loop()
    await DnsWayUdpResolver().start(loop)


if __name__ == "__main__":
    asyncio.run(main())
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.dns.message.dns_message import DnsMessage
import asyncio
import socket
import time


class NetworkResolverService():

    async def send_msg(self, raw_req_msg:DnsMessage, future, address, callback, port=53):
        try:
            print("sending to:",address)
            transport, protocol = await asyncio.get_running_loop().create_datagram_endpoint(lambda: UDPClientProtocol(future, address, callback),remote_addr=(address, port),family=socket.AF_INET6 if ':' in address else socket.AF_INET)
            transport.sendto(raw_req_msg.encode())
            # response = await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            await callback(address, 100, True)
        except OSError as ose: # called when ipv4 network interface or ipv6 not available
            pass

    async def resolve(self, addresses, raw_req_msg, callback:callable):
        future = asyncio.get_running_loop().create_future()
        tasks = [asyncio.create_task(self.send_msg(raw_req_msg, future, addr, callback)) for addr in addresses]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        res_msg = await future
        # await asyncio.gather(*pending)
        return DnsMessageConverter().to_view(res_msg)


class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, future, address, callback):
        self.future = future
        self.address = address
        self.callback = callback
        self._start_time = 0

    def connection_made(self, transport):
        self.transport = transport
        self._start_time = time.time()

    def datagram_received(self, data, addr):
        elapsed_time = time.time() - self._start_time
        print("received response from",addr)
        asyncio.create_task(self.callback(addr,elapsed_time,False))
        if not self.future.done():
            res_msg = DnsMessage.Decode(data)
            self.future.set_result(res_msg)
        self.transport.close()
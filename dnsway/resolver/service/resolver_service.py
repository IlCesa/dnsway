import asyncio
import socket
import time
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.resource import ResourceRecordFormat
from dnsway.dns.message.utils.converter import DnsMessageConverter, ResourceRecordConverter
from dnsway.dns.message.utils.dns_message_view import ARecordView, DnsMessageView, RRecordView
from dnsway.dns.transport.dns_transport import TRANSPORT_MODE, DnsWayTransportFactory
from dnsway.resolver.adapter.sbelt_repository import SBeltRepository
from dnsway.resolver.domain.resolver_model import NameServer, QueryResolutionHistory
from dnsway.resolver.service.unit_of_work import AbstractUnitOfWork, QueryHistoryUnitOfWork
import abc


class AbstractServiceLayer:
    @abc.abstractmethod
    def process(self) -> DnsMessage:
        raise NotImplementedError


class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, future, address, callback):
        self.future = future
        self.address = address
        self.callback = callback
        self._start_time = 0

    def connection_made(self, transport):
        self.transport = transport
        self._start_time = time.time()

    # def connection_lost(self, exc):
    #     return super().connection_lost(exc)

    def datagram_received(self, data, addr):
        # print(f"received from {addr} {data}")
        elapsed_time = time.time() - self._start_time
        asyncio.create_task(self.callback(addr,elapsed_time,False))

        res_msg = DnsMessage.Decode(data)
        if not self.future.done():
            self.future.set_result(res_msg)
        self.transport.close()

class NetworkResolverService():

    async def send_msg(self, raw_req_msg:DnsMessage, future, address, callback, port=53):
        try:
            transport, protocol = await asyncio.get_running_loop().create_datagram_endpoint(
                lambda: UDPClientProtocol(future, address, callback),
                remote_addr=(address, port),
                family=socket.AF_INET6 if ':' in address else socket.AF_INET,
            )
            # print("sending to",address)
            transport.sendto(raw_req_msg.encode())
            # response = await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            await callback(address, 100, True)
        except OSError as ose: # called when ipv4 network interface or ipv6 not available
            # print("OS ERROR CAUGHT",ose)
            pass

    async def resolve(self, addresses, raw_req_msg, callback:callable):
        future = asyncio.get_running_loop().create_future()
        tasks = [self.send_msg(raw_req_msg, future, addr, callback) for addr in addresses]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        # print("completato")
        res_msg = await future
        return DnsMessageConverter().to_view(res_msg)
    

class DnsServerResolverServiceImpl(AbstractServiceLayer):
    def __init__(self, query_history_of_work:QueryHistoryUnitOfWork):
        self.query_history_uow = query_history_of_work
        self.network_resolver_service = NetworkResolverService()
        self.processed_domains_list = []

        self.query_key = None #will be initialized once process method is called

    async def __update_ns_stats_callback(self, address:str, elapsed_time:float, timed_out:bool) -> None:
        # print("CALLED BACK FROM COROUTINE", address[0], elapsed_time, timed_out)
        address, port = address
        async with self.query_history_uow as qru:
            qrh:QueryResolutionHistory = qru.history.get(*self.query_key)
            ns: NameServer = qrh.get_ns_by_address(address)
            # print("FROM CALLBACK FOUND NS:",ns)
            if ns != -1:
                ns.increment_req()
                if not timed_out:
                    ns.increment_res()
                    ns.add_t(elapsed_time)
                    print("NS STATS FOR",address,"UPDATED SUCCESFULLY")

    async def process(self, dns_message_view:DnsMessageView) -> DnsMessage:
        try:
            question = dns_message_view.question
            stuple = (question.name, question.type_value, question.class_value)
            self.query_key = stuple
            answers = await self.__global_lookup(*stuple)
            answers = answers[1]
            # for answer in answers:
            #     print(answer.name, answer.type_value, answer.class_value, answer.ttl, answer.data)
            dns_message_view.header.ra = True
            dns_message_view.header.qr = QUERY_TYPE.RESPONSE
            dns_message_view.answer_list = answers
            return dns_message_view

        except Exception as e:
            print("Process exception error: ", e)
            return DnsServerResolverServiceImpl.DnsMessageNotImplemented(dns_message_view.header.id, dns_message_view.question.name)

    async def __global_lookup(self, sname:str, stype:QTYPE_VALUES, sclass:QCLASS_VALUES) -> list[RRecordView]:
        initial_sname = sname
        rr_found = False
        rr_list = []
        while not rr_found:
            res = -1
            cache_response = False
            async with self.query_history_uow as qru:
                qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                res = qrh.local_lookup()

            if res != -1:
                cache_response = True
                answers = res
            else:  
                async with self.query_history_uow as qru:
                    qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                    na:NameServer = qrh.next_address(desired_addresses=4)
                    addresses = [ns.address for ns in na]
                    # print(f"Next address:{addresses}")
                msg = (DnsMessageBuilderNew().header(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY).question(qname=sname, qtype=stype, qclass=sclass).build())
                recv_iteration_message_view = await self.network_resolver_service.resolve(addresses, msg, self.__update_ns_stats_callback)

                # print("RECV MSG")
                # print(recv_iteration_message_view)
                answers = recv_iteration_message_view.answer_list
                autorithies = recv_iteration_message_view.autorithy_list
                additionals = recv_iteration_message_view.additional_list

            if answers:
                for answer in answers:
                    if stype == answer.type_value:
                        rr_list.append(answer)
                        rr_found = True
                        if not cache_response:
                            async with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache_rrecord(answer)
                                # qrh.cache.append(answer)

                    elif answer.type_value == QTYPE_VALUES.CNAME:
                        #TODO: CHECK IN THE ADDITIONAL SECTION IF THERE IS A GLUE RECORD FOR THIS CNAME
                        # ESEMPIO -> in answer troviamo C.ISI.EDU. -> in AUTORITHY troviamo l'NS SERVER ISI.EDU. E IN ADDITIONAL TROVIAMO IL RECORD A PER ISI.EDU.
                        if not cache_response:
                            async with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache_rrecord(answer)

                        sname = answer.data.alias
                        rr_list.append(answer)

            elif additionals:
                slist = []
                for additional in additionals:
                    slist.append(NameServer(additional.name, additional.data.address, additional.ttl))
                
                async with self.query_history_uow as qru:
                    qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                    qrh.set_slist(slist)

            elif autorithies:
                task_list = []
                for autorithy in autorithies:
                    task_list.append(self.__global_lookup(autorithy.data.nsdname, QTYPE_VALUES.A, QCLASS_VALUES.IN))
                
                done, pending = await asyncio.wait(task_list, return_when=asyncio.ALL_COMPLETED)
                # dovrei iterare su tutta la lista qui per poter aggiungere tutte le nuove delegazioni eventualmente responsabili per la risoluzione della seguente query
                # probema -> aspettare tutti riduce il tempo totale di risoluzione (la prima volta) ma ci da' piu' opzioni per le risoluzioni successive (una volta cachate)
                slist = []
                while len(done) > 0:
                    nsdname, ns_list = done.pop().result()
                    print(nsdname, ns_list)
                    slist.extend([NameServer(nsdname, nsrecord.data.address) for nsrecord in ns_list])
                async with self.query_history_uow as qru:
                        qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                        qrh.set_slist(slist)
            else:
                raise Exception('NO RESPONSE FOUND')

        return (initial_sname, rr_list)


    @staticmethod
    def DnsMessageNotImplemented(id:int, domain_name:str) -> DnsMessage:
        msg = (DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.NOT_IMPLEMENTED,opcode=OPCODE_TYPE.QUERY)
                .question(qname=domain_name, qtype=QTYPE_VALUES.A, qclass=QCLASS_VALUES.IN)
                .build())
        return DnsMessageConverter().to_view(msg)


    @staticmethod
    def DnsMessageNameError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.NAME_ERROR).build()
        return DnsMessageConverter().to_view(msg)
    

    @staticmethod
    def DnsMessageFormatError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.FORMAT_ERROR).build()
        return DnsMessageConverter().to_view(msg)


    @staticmethod
    def DnsMessageServerFailure(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.SERVER_FAILURE).build()
        return DnsMessageConverter().to_view(msg)
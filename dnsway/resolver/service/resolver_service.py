import asyncio
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
    def __init__(self, future, address):
        self.future = future
        self.address = address

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # print(f"received from {addr} {data}", flush=True)
        res_msg = DnsMessage.Decode(data)
        if not self.future.done():
            self.future.set_result(res_msg)
        self.transport.close()

class NetworkResolverService():
    def __init__(self):
        pass
        #self.event_loop = event_loop

    async def send_msg(self, raw_req_msg:DnsMessage, future, address, port=53):
        transport, protocol = await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: UDPClientProtocol(future, address),
            remote_addr=(address, port)
        )
        # converto il messaggio in byte
        print("sending to",address)

        transport.sendto(raw_req_msg.encode())  
        # try:
        #     await future  # Attendi che venga impostato il risultato
        # finally:
        #     transport.close()

    async def resolve(self, addresses, raw_req_msg):
        future = asyncio.get_running_loop().create_future()
        print("sono qui")
        tasks = [self.send_msg(raw_req_msg, future, addr) for addr in addresses]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        print("completato")
        # for task in pending:
        #     task.cancel()
        # await asyncio.gather(*pending)
        res_msg = await future
        print(res_msg)
        return DnsMessageConverter().to_view(res_msg)

class DnsServerResolverServiceImpl(AbstractServiceLayer):
    def __init__(self, query_history_of_work:QueryHistoryUnitOfWork):
        self.query_history_uow = query_history_of_work
        self.network_resolver_service = NetworkResolverService()
        self.processed_domains_list = []

    async def process(self, dns_message_view:DnsMessageView) -> DnsMessage:
        try:
            # print("\n\n\n\n\n\n\n\n\n\n\n\n\n")
            # print("RECV REQ:")
            # print(dns_message_view)
            question = dns_message_view.question
            stuple = (question.name, question.type_value, question.class_value, dns_message_view.header.id)
            answers = await self.__search_records(*stuple)
            answers = answers[1]
            for answer in answers:
                print(answer.name, answer.type_value, answer.class_value, answer.ttl, answer.data)

            #print("risposta:",answers)
            return DnsServerResolverServiceImpl.DnsMessageNotImplemented(dns_message_view.header.id, dns_message_view.question.name)

        except Exception as e:
            print(e)
            return DnsServerResolverServiceImpl.DnsMessageNotImplemented(dns_message_view.header.id, dns_message_view.question.name)

    async def __search_records(self, sname:str, stype:QTYPE_VALUES, sclass:QCLASS_VALUES, id:int=None) -> list[RRecordView]:
        initial_sname = sname
        rr_found = False
        rr_list = []
        while not rr_found:
            res = -1
            cache_response = False
            with self.query_history_uow as qru:
                qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                res = qrh.local_lookup()

            if res != -1:

                cache_response = True
                answers = res
            else:  
                with self.query_history_uow as qru:
                    qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                    na:NameServer = qrh.next_address()
                    addresses = [ns.address for ns in na]
                    print(f"Next address:{addresses}")

                msg = (DnsMessageBuilderNew().header(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY).question(qname=sname, qtype=stype, qclass=sclass).build())
                recv_iteration_message_view = await self.network_resolver_service.resolve(addresses, msg)

                #print("RECV MSG")
                #print(recv_iteration_message_view)
                answers = recv_iteration_message_view.answer_list
                autorithies = recv_iteration_message_view.autorithy_list
                additionals = recv_iteration_message_view.additional_list

            if answers:
                for answer in answers:
                    if stype == answer.type_value:
                        rr_list.append(answer)
                        rr_found = True
                        if not cache_response:
                            with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache.append(answer)

                    elif answer.type_value == QTYPE_VALUES.CNAME:
                        #TODO: CHECK IN THE ADDITIONAL SECTION IF THERE IS A GLUE RECORD FOR THIS CNAME
                        # ESEMPIO -> in answer troviamo C.ISI.EDU. -> in AUTORITHY troviamo l'NS SERVER ISI.EDU. E IN ADDITIONAL TROVIAMO IL RECORD A PER ISI.EDU.
                        if not cache_response:
                            with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache.append(answer)

                        sname = answer.data.alias
                        rr_list.append(answer)

            elif additionals:
                slist = []
                for additional in additionals:
                    slist.append(NameServer(additional.name, additional.data.address, additional.ttl))
                    with self.query_history_uow as qru:
                        qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                        qrh.set_slist(slist)

            elif autorithies:
                task_list = []
                for autorithy in autorithies:
                    task_list.append(self.__search_records(autorithy.data.nsdname, QTYPE_VALUES.A, QCLASS_VALUES.IN))
                
                done, pending = await asyncio.wait(task_list, return_when=asyncio.FIRST_COMPLETED)
                nsdname, ns_list = done.pop().result()
                slist = [NameServer(nsdname, nsrecord.data.address) for nsrecord in ns_list[:1]]
                with self.query_history_uow as qru:
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
        msg = DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.NAME_ERROR).build()
        return DnsMessageConverter().to_view(msg)
    

    @staticmethod
    def DnsMessageFormatError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.FORMAT_ERROR).build()
        return DnsMessageConverter().to_view(msg)

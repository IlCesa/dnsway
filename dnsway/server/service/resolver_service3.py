import copy
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.resource import ResourceRecordFormat
from dnsway.dns.message.utils.converter import DnsMessageConverter, ResourceRecordConverter
from dnsway.dns.message.utils.dns_message_view import DnsMessageView, RRecordView
from dnsway.dns.transport.dns_transport import TRANSPORT_MODE, DnsWayTransportFactory
from dnsway.server.adapter.cache_repository import AbstractCacheRepository
from dnsway.server.adapter.rootserver_repository import AbstractRootRepository
from dnsway.server.domain.resolver_model import RequestResourceState, RootServer
import abc

from dnsway.server.service.unit_of_work import AbstractUnitOfWork


class AbstractServiceLayer:
    @abc.abstractmethod
    def process(self) -> DnsMessage:
        raise NotImplementedError


class DnsServerResolverServiceImpl(AbstractServiceLayer):
    
    # qui sara' passato uow instance invece che il repository
    def __init__(self, rootserver_repository:AbstractRootRepository, cache_unit_of_work:AbstractUnitOfWork):
        self.rootserver_repository = rootserver_repository
        self.cache_uow = cache_unit_of_work
        self.processed_domains_list = []


    def process(self, dns_message_view:DnsMessageView) -> DnsMessage:
        try:
            # check cache here
            question = dns_message_view.question
            stuple = (question.name, question.type_value, question.class_value, dns_message_view.header.id)
            return self.__search_records(*stuple)
        except Exception:
            return DnsServerResolverServiceImpl.DnsMessageNotImplemented(dns_message_view.header.id, dns_message_view.question.name)


    def __search_records(self, sname, stype, sclass, id=None):
        response = (DnsMessageBuilderNew().header(id=id, qr=QUERY_TYPE.RESPONSE,opcode=OPCODE_TYPE.QUERY,rd=True, ra=True).question(qname=sname, qtype=stype, qclass=sclass))
        address = self.rootserver_repository.get().ipv4

        # with self.cache_uow:
        # sara' in un dizionario
        rrs = RequestResourceState(sname,stype,sclass)
            # self.cache_uow.commit()

        found = False
        while not found:
            msg = (DnsMessageBuilderNew().header(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY).question(qname=sname, qtype=stype, qclass=sclass).build())


            dnsway_trasport = DnsWayTransportFactory().create_transport(transport_mode=TRANSPORT_MODE.DATAGRAM,address=address,port=53)
            dnsway_trasport.send(msg)
            recv_iteration_message:DnsMessage = dnsway_trasport.recv()
            recv_iteration_message_view = DnsMessageConverter().to_view(recv_iteration_message)

            print("RECV MSG")
            print(recv_iteration_message_view)
            # time.sleep(5)
            answers = recv_iteration_message_view.answer_list
            autorithies = recv_iteration_message_view.autorithy_list
            additionals = recv_iteration_message_view.additional_list

            #ITERO SULLA LISTA DEI RECORD RICEVUTI NELLA RISPOSTA
            # SE MATCHA IL RECORD RICEVUTO LO COPIO NELLA RISPOSTA
            # ALTRIMENTI CONSIDERO EVENTUALI CNAME

            if answers:
                for answer in answers:
                    rrecord = answer.data
                    if stype == answer.type_value:
                        found = True
                        rdata = ResourceRecordConverter().to_msg(rrecord)
                        response.answer(answer.name, answer.type_value, answer.class_value, answer.ttl, rdata)
                    elif answer.type_value == QTYPE_VALUES.CNAME:
                        # dovrei controllare se c'è per questo cname un NS direttamente disponibile
                        # nelle autorithy list e, di conseguenza, se c'è il glue record nell'additional
                        # ESEMPIO -> in answer troviamo C.ISI.EDU. -> in AUTORITHY troviamo l'NS SERVER ISI.EDU. E IN ADDITIONAL TROVIAMO IL RECORD A PER ISI.EDU.
                        sname = rrecord.alias
                        rdata = ResourceRecordConverter().to_msg(rrecord)
                        response.answer(answer.name, answer.type_value, answer.class_value, answer.ttl, rdata)
                        address = self.rootserver_repository.get().ipv4
            elif autorithies:
                additionals_dict = {}
                # devo prendere sia A records che AAAA
                for k in additionals:
                    if k.type_value == QTYPE_VALUES.A:
                        additionals_dict[k.name] = k

                for autorithy in autorithies:
                    nsrecord = autorithy.data
                    if nsrecord.nsdname in additionals_dict:
                        arecord = additionals_dict[nsrecord.nsdname]
                        if arecord.type_value == QTYPE_VALUES.A: # ipv6 not supported yet
                            address = arecord.data.address
                            #addresses.append(arecord.data.address)
                    else:
                        k = self.__search_records(autorithy.data.nsdname,'A','IN')
                        msg = DnsMessageConverter().to_view(k)
                        address = msg.answer_list[0].data.address
                        break
            else:
                raise Exception('NO RESPONSE FOUND')

        return DnsMessageConverter.to_view(response.build())


    @staticmethod
    def DnsMessageNotImplemented(id:int, domain_name:str) -> DnsMessage:
        msg =  (DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.NOT_IMPLEMENTED,opcode=OPCODE_TYPE.QUERY)
                .question(qname=domain_name, qtype=QTYPE_VALUES.A, qclass=QCLASS_VALUES.IN)
                .build())
        return DnsMessageConverter().to_msg(msg)


    @staticmethod
    def DnsMessageNameError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.NAME_ERROR).build()
        return DnsMessageConverter().to_msg(msg)
    

    @staticmethod
    def DnsMessageFormatError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.FORMAT_ERROR).build()
        return DnsMessageConverter().to_msg(msg)

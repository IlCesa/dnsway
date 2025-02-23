import time
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.resource import ResourceRecordFormat
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.dns.message.utils.dns_message_view import DnsMessageView, RRecordView
from dnsway.dns.transport.dns_transport import TRANSPORT_MODE, DnsWayTransportFactory
from dnsway.server.adapter.cache_repository import AbstractCacheRepository
from dnsway.server.adapter.rootserver_repository import AbstractRootRepository
from dnsway.server.domain.resolver_model import RootServer
import abc


class AbstractServiceLayer:
    @abc.abstractmethod
    def process(self) -> DnsMessage:
        raise NotImplementedError


class DnsServerResolverServiceImpl(AbstractServiceLayer):
    
    def __init__(self, rootserver_repository:AbstractRootRepository, cache_repository:AbstractCacheRepository):
        self.rootserver_repository = rootserver_repository
        self.cache_repository = cache_repository

        self.processed_domains_list = []


    def process(self, data) -> DnsMessage:
        user_request_message = DnsMessage.Decode(data)
        print(user_request_message)
        sname = user_request_message.question.qname.domain_name
        try:
            # check cache here
            res = self.__search_authoritative(sname)
            dns_message_view:DnsMessageView = DnsMessageConverter().raw_msg_to_view(res)
            print(dns_message_view)
            res.header.id = user_request_message.header.id.value
            res.header.ra = True
            res.header.rd = True
            res.hex_dump()
            # res.answer.rrformat_list[0].rdata_length = 29
            print("valore cname",res.answer.rrformat_list[0].rdata_length)
            #print("lunghezza in byte",len(res.encode()))
            return res
        except Exception as e:
            print(e)
            return DnsServerResolverServiceImpl.DnsMessageNotImplemented(user_request_message.header.id.value,user_request_message.question.qname.domain_name)

    def __search_authoritative(self, domain_name):
        recv_iteration_message = DnsMessage()
        stype = QTYPE_VALUES.A
        sname = domain_name
        response = (DnsMessageBuilderNew(qr=QUERY_TYPE.RESPONSE,opcode=OPCODE_TYPE.QUERY).question(qname=domain_name, qtype="A", qclass="IN"))
        
        address = self.rootserver_repository.get().ipv4
        found = False
        while not found:
            msg = (DnsMessageBuilderNew(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY).question(qname=domain_name, qtype="A", qclass="IN").build())
            dnsway_trasport = DnsWayTransportFactory().create_transport(transport_mode=TRANSPORT_MODE.DATAGRAM,address=address,port=53)
            print("sending to address",address)
            dnsway_trasport.send(msg)
    
            # CONVERTING TO MSG_VIEW
            recv_iteration_message:DnsMessage = dnsway_trasport.recv()
            recv_iteration_message_view:DnsMessageView = DnsMessageConverter().raw_msg_to_view(recv_iteration_message)
            
            recv_answer : RRecordView = recv_iteration_message_view.answer_list
            recv_additional = recv_iteration_message_view.additional_list
            recv_autorithy = recv_iteration_message_view.autorithy_list

            if len(recv_answer) > 0:
                if stype == recv_answer[0].type_value:
                    print("Aggiungo alla risposta: ", recv_answer[0].data)
                    found = True

                    answer_rrformat:ResourceRecordFormat = recv_iteration_message.answer.rrformat_list[0]
                    domain_name = answer_rrformat.name.domain_name
                    type_value = QTYPE_VALUES(answer_rrformat.type_value.value)
                    class_value = QCLASS_VALUES(answer_rrformat.class_value.value)
                    ttl = answer_rrformat.ttl.value
                    rdata = answer_rrformat.rdata.resource_record
                    response.answer(domain_name, type_value, class_value, ttl, rdata)
                    found_ip =  recv_answer[0].data 
                else:
                    if recv_answer[0].type_value == QTYPE_VALUES.CNAME:
                        print("è un cname cazzo faccio")
                        #print(recv_iteration_message.answer.rrformat_list[0].hex_dump())
                        #recv_iteration_message.answer.rrformat_list[0]

                        cname_rrformat:ResourceRecordFormat = recv_iteration_message.answer.rrformat_list[0]
                        domain_name = cname_rrformat.name.domain_name
                        type_value = QTYPE_VALUES(cname_rrformat.type_value.value)
                        class_value = QCLASS_VALUES(cname_rrformat.class_value.value)
                        ttl = cname_rrformat.ttl.value
                        rdata = cname_rrformat.rdata.resource_record

                        response.answer(domain_name, type_value, class_value, ttl, rdata)
                        # time.sleep(10)
                        # HO CAPITO COSA STA SUCCEDENDO.
                        # IO STO COPIANDO
                        
                        #response.answer(recv_iteration_message.answer.rrformat_list[0])
                        domain_name = recv_answer[0].data
                        print(domain_name)
                        # time.sleep(3)
                        address = self.rootserver_repository.get().ipv4
                    
            elif len(recv_additional) == 0:
                k = self.__search_authoritative(recv_autorithy[0].data)
                address = DnsMessageConverter().raw_msg_to_view(k).answer_list[0].data
                print("address autoritativo: ",address)
            else:
                for k in recv_additional:
                    if k.type_value == QTYPE_VALUES.A:
                        address = k.data
                        break
        print(found_ip)
        print("qui")
        return response.build()


    @staticmethod
    def DnsMessageNotImplemented(id:int, domain_name:str) -> DnsMessage:
        return (DnsMessageBuilderNew(rd=True,id=id, rcode=RCODE_TYPE.NOT_IMPLEMENTED,opcode=OPCODE_TYPE.QUERY)
                .question(qname=domain_name, qtype=QTYPE_VALUES.A, qclass=QCLASS_VALUES.IN)
                .build())


    @staticmethod
    def DnsMessageNameError(id:int) -> DnsMessage:
        return DnsMessageBuilderNew(rd=True,id=id, rcode=RCODE_TYPE.NAME_ERROR).build()
    

    @staticmethod
    def DnsMessageFormatError(id:int) -> DnsMessage:
        return DnsMessageBuilderNew(rd=True,id=id, rcode=RCODE_TYPE.FORMAT_ERROR).build()
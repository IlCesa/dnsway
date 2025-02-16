from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.dns.message.utils.dns_message_view import DnsMessageView
from dnsway.dns.transport.dns_transport import TRANSPORT_MODE, DnsWayTransportFactory
from dnsway.server.domain.model import RootServer
import abc


class AbstractServiceLayer:
    @abc.abstractmethod
    def process(self) -> DnsMessage:
        raise NotImplementedError


class DnsServerResolverServiceImpl(AbstractServiceLayer):
    
    def __init__(self, rootserver_repository):
        self.rootserver_repository = rootserver_repository

    def process(self, data) -> DnsMessage:
        try:
            print(self.rootserver_repository.get())
            dns_resolver_response = DnsMessage()
            user_request_message = DnsMessage()
            user_request_message.decode(data)

            # user_request_message.hex_dump()
            #print(message.question.qname.domain_name)
            print("domain_name:",user_request_message.question.qname.domain_name)
            print("authoritative server ip:",self.__search_autorithative(user_request_message.question.qname.domain_name))
            address = self.__search_autorithative(user_request_message.question.qname.domain_name)

            msg = (DnsMessageBuilderNew(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY,rd=True)
                    .question(qname=user_request_message.question.qname.domain_name, qtype="A", qclass="IN")
                    .build())
            
            dnsway_trasport = DnsWayTransportFactory().create_transport(transport_mode=TRANSPORT_MODE.DATAGRAM,address=address,port=53)
            dnsway_trasport.send(msg)
            return dnsway_trasport.recv()
            # recv_iteration_message = DnsMessage()
            # phase = 1
            # print("aa",recv_iteration_message.header.aa)
            
            # processed_domains_dict = {}
            # while not recv_iteration_message.header.aa:
            #     # dns_message_view:DnsMessageView = DnsMessageConverter().raw_msg_to_view(recv_iteration_message)
            #     # # print(dns_message_view)
            #     # if len(dns_message_view.additional_list) == 0:
            #     #     address = self.rootserver_repository.get().ipv4
            #     #     phase = 0
                
            #     # address = dns_message_view.additional_list[0].data

            #     dnsway_trasport = DnsWayTransportFactory().create_transport(transport_mode=TRANSPORT_MODE.DATAGRAM,address=address,port=53)
            #     dnsway_trasport.send(msg)
            #     recv_iteration_message = dnsway_trasport.recv()
            #     phase = phase + 1
            #     print(recv_iteration_message.hex_dump())

            # print("ok ricevuta risposta autoritativa")
            # translate req to a new msg
            # send the new message
            # wait the response
            # dns_resolver_response = DnsServerResolverServiceImpl.DnsMessageNotImplemented(message.header.id.value,message.question.qname.domain_name)
            return dns_resolver_response
        except Exception as e:
            print(e)

    def __search_autorithative(self, domain_name):
        phase = 0
        recv_iteration_message = DnsMessage()
        while not recv_iteration_message.header.aa:
            address = self.rootserver_repository.get().ipv4
            if phase >=1:
                recv_iteration_message_view:DnsMessageView = DnsMessageConverter().raw_msg_to_view(recv_iteration_message)
                if len(recv_iteration_message_view.additional_list) == 0:
                    print(recv_iteration_message_view.autorithy_list[0].data)
                    return self.__search_autorithative(recv_iteration_message_view.autorithy_list[0].data)
                else:
                    address = recv_iteration_message_view.additional_list[0].data

            msg = (DnsMessageBuilderNew(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY,rd=True)
                    .question(qname=domain_name, qtype="A", qclass="IN")
                    .build())
            print("send req to address",address)
            dnsway_trasport = DnsWayTransportFactory().create_transport(transport_mode=TRANSPORT_MODE.DATAGRAM,address=address,port=53)
            dnsway_trasport.send(msg)
            recv_iteration_message = dnsway_trasport.recv()
            dns_message_view:DnsMessageView = DnsMessageConverter().raw_msg_to_view(recv_iteration_message)
            print(dns_message_view)
            phase = phase+1
        
        return dns_message_view.answer_list[0].data

        

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
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
from dnsway.server.domain.resolver_model import RootServer
import time
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
        # qui devo ricevere direttamente un DnsMessageView.
        # per comodita' questo servizio, ovvero colui che si occupa di processare la richiesta
        # non deve lavorare col messaggio raw (quello è responsabilita' del controller/network service)
        # stessa cosa per il valore di ritorno, dovra' essere un DnsMessageView

        user_request_message = DnsMessage.Decode(data)
        req_id = user_request_message.header.id.value
        sname = user_request_message.question.qname.domain_name

        # print(user_request_message)

        try:
            # check cache here
            res = self.__search_records(sname)
            res.hex_dump()

            # dns_message_view:DnsMessageView = DnsMessageConverter().to_view(res)
            # # print(dns_message_view)
            # dns_message = DnsMessageConverter().to_msg(dns_message_view=dns_message_view)
            # dns_message.hex_dump()
            
            res.header.id = user_request_message.header.id.value
            res.header.ra = True
            res.header.rd = True
            return res
        except Exception as e:
            return DnsServerResolverServiceImpl.DnsMessageNotImplemented(req_id,sname)

    def __search_records(self, domain_name):

        stype = QTYPE_VALUES.A
        sname = domain_name

        response = (DnsMessageBuilderNew().header(qr=QUERY_TYPE.RESPONSE,opcode=OPCODE_TYPE.QUERY).question(qname=domain_name, qtype=stype, qclass="IN"))
        
        # address dovra' essere una lista
        address = self.rootserver_repository.get().ipv4
        addresses = [self.rootserver_repository.get().ipv4]

        # recv_iteration_message = DnsMessage()
        found = False
        while not found:
            msg = (DnsMessageBuilderNew().header(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY).question(qname=domain_name, qtype="A", qclass="IN").build())
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

            if len(answers) > 0:
                for answer in answers:
                    rrecord = answer.data
                    if stype == answer.type_value:
                        found = True
                        rdata = copy.deepcopy(ResourceRecordConverter().to_msg(rrecord))
                        response.answer(answer.name, answer.type_value, answer.class_value, answer.ttl, rdata)
                    elif answer.type_value == QTYPE_VALUES.CNAME:
                        # dovrei controllare se c'è per questo cname un NS direttamente disponibile
                        # nelle autorithy list e, di conseguenza, se c'è il glue record nell'additional
                        # ESEMPIO -> in answer troviamo C.ISI.EDU. -> in AUTORITHY troviamo l'NS SERVER ISI.EDU. E IN ADDITIONAL TROVIAMO IL RECORD A PER ISI.EDU.
                        domain_name = rrecord.alias
                        rdata = ResourceRecordConverter().to_msg(rrecord)
                        response.answer(answer.name, answer.type_value, answer.class_value, answer.ttl, rdata)
                        address = self.rootserver_repository.get().ipv4
            elif len(autorithies) > 0:
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

                        k = self.__search_records(autorithy.data.nsdname)
                        msg = DnsMessageConverter().to_view(k)
                        address = msg.answer_list[0].data.address
                        break
            else:
                raise Exception('NO RESPONSE FOUND')



            # if len(recv_answer) > 0:
            #     for answer in recv_iteration_message_view.answer_list:
            #         if stype == answer.type_value:
            #             # print("Aggiungo alla risposta: ", answer.data)
            #             found = True
            #             answer_rrformat:ResourceRecordFormat = recv_iteration_message.answer.rrformat_list[0]
            #             domain_name = answer_rrformat.name.domain_name
            #             type_value = QTYPE_VALUES(answer_rrformat.type_value.value)
            #             class_value = QCLASS_VALUES(answer_rrformat.class_value.value)
            #             ttl = answer_rrformat.ttl.value
            #             rdata = answer_rrformat.rdata.resource_record
            #             # print(type(rdata))
            #             response.answer(domain_name, type_value, class_value, ttl, rdata)
            #             found_ip =  recv_answer[0].data 
            #         else:
            #             if answer.type_value == QTYPE_VALUES.CNAME:
            #                 # # print("è un cname cazzo faccio")
            #                 ## print(recv_iteration_message.answer.rrformat_list[0].hex_dump())
            #                 #recv_iteration_message.answer.rrformat_list[0]

            #                 cname_rrformat:ResourceRecordFormat = recv_iteration_message.answer.rrformat_list[0]
            #                 domain_name = cname_rrformat.name.domain_name
            #                 type_value = QTYPE_VALUES(cname_rrformat.type_value.value)
            #                 class_value = QCLASS_VALUES(cname_rrformat.class_value.value)
            #                 ttl = cname_rrformat.ttl.value
            #                 rdata = cname_rrformat.rdata.resource_record
            #                 # print(type(rdata))
            #                 response.answer(domain_name, type_value, class_value, ttl, rdata)
            #                 # time.sleep(10)
            #                 # HO CAPITO COSA STA SUCCEDENDO.
                            
            #                 #response.answer(recv_iteration_message.answer.rrformat_list[0])
            #                 domain_name = recv_answer[0].data.alias
            #                 # print("alias to search:",type(domain_name))
            #                 # time.sleep(3)
            #                 address = self.rootserver_repository.get().ipv4
            # # NUOVA LOGICA DI CONTROLLO
            # # da qui in poi sarebbe piu' corretto avere questa struttura
            # # check lista autority > 0 => controllo glue records in additional list => contatto gli address forniti come glue records
            # # se non ci sono dati come autority beh, BadResponse o NameServerError
            # elif len(recv_additional) == 0:
            #     k = self.__search_records(recv_autorithy[0].data.nsdname)
            #     address = DnsMessageConverter().to_view(k).answer_list[0].data.address
            #     # print("address autoritativo: ",address)
            # else:
            #     for k in recv_additional:
            #         if k.type_value == QTYPE_VALUES.A:
            #             address = k.data.address
            #             break
        # # print(found_ip)
        return response.build()


    @staticmethod
    def DnsMessageNotImplemented(id:int, domain_name:str) -> DnsMessage:
        return (DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.NOT_IMPLEMENTED,opcode=OPCODE_TYPE.QUERY)
                .question(qname=domain_name, qtype=QTYPE_VALUES.A, qclass=QCLASS_VALUES.IN)
                .build())


    @staticmethod
    def DnsMessageNameError(id:int) -> DnsMessage:
        return DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.NAME_ERROR).build()
    

    @staticmethod
    def DnsMessageFormatError(id:int) -> DnsMessage:
        return DnsMessageBuilderNew().header(rd=True,id=id, rcode=RCODE_TYPE.FORMAT_ERROR).build()

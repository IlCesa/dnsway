# from __future__ import annotations
from __future__ import annotations
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.exception import DnsWayMultipleQuestionNotSupported
from dnsway.dns.message.resource import ResourceRecordFormat, ResourceRecordMessage
from dnsway.dns.message.question import QuestionMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE, HeaderMessage

class DnsMessage(DnsWaySerializer):

    def __init__(self):
        self.header     : HeaderMessage          =  HeaderMessage()
        self.question   : QuestionMessage        =  QuestionMessage()
        self.answer     : ResourceRecordMessage  =  ResourceRecordMessage(count=self.header.ancount, label='Answer')
        self.autorithy  : ResourceRecordMessage  =  ResourceRecordMessage(count=self.header.nscount, label='Autorithy')
        self.additional : ResourceRecordMessage  =  ResourceRecordMessage(count=self.header.arcount, label='Additional')
        
        super().__init__(label = 'DnsMessage')


    def encode(self, /) -> bytearray:
        return super().encode(self.header, self.question, self.answer, self.autorithy, self.additional)
    
    
    def decode(self, data:bytearray, offset:int = 0, /) -> int:
        return super().decode(data, offset, self.header, self.question, self.answer, self.autorithy, self.additional)


class DnsMessageBuilderNew():
    def __init__(self, rd:bool=False, ra:bool=False, aa:bool=False, tc:bool=False, opcode:OPCODE_TYPE=OPCODE_TYPE.QUERY, qr:QUERY_TYPE=QUERY_TYPE.QUERY,
                 id:int=None, rcode:RCODE_TYPE=RCODE_TYPE.NO_ERROR):
        self.__dns_message = DnsMessage()
        self.__dns_message.header.query_type = qr
        self.__dns_message.header.rd = rd
        self.__dns_message.header.ra = ra
        self.__dns_message.header.aa = aa
        self.__dns_message.header.tc = tc
        self.__dns_message.header.opcode = opcode
        self.__dns_message.header.rcode = rcode

        if id is not None:
            self.__dns_message.header.id = id


    def __build_rrformat(self, name:str, type_value:str|QTYPE_VALUES, class_value:str|QCLASS_VALUES, ttl:int, rdata):
        rrformat = ResourceRecordFormat()
        rrformat.name = name
        rrformat.type_value = QTYPE_VALUES[type_value] if type(type_value) == str else type_value
        rrformat.class_value = QCLASS_VALUES[class_value] if type(type_value) == str else class_value
        rrformat.ttl = ttl
        rrformat.rdata = rdata
        return rrformat
    

    def question(self, qname:str, qtype:str|QTYPE_VALUES, qclass:str|QCLASS_VALUES):
        if self.__dns_message.header.qdcount == 1:
            raise DnsWayMultipleQuestionNotSupported()
        
        self.__dns_message.question.qname  = qname
        self.__dns_message.question.qtype  =  QTYPE_VALUES[qtype] if type(qtype) == str else qtype
        self.__dns_message.question.qclass = QCLASS_VALUES[qclass] if type(qclass) == str else qclass
        self.__dns_message.header.qdcount = 1

        return self


    def answer(self, name, type_value, class_value, ttl, rdata):
        self.__dns_message.header.ancount = self.__dns_message.header.ancount.value+1
        self.__dns_message.answer.rrformat_list.append(self.__build_rrformat(name, type_value, class_value, ttl, rdata))
        return self


    def autorithy(self, name, type_value, class_value, ttl, rdata=None):
        self.__dns_message.autorithy.rrformat_list.append(self.__build_rrformat(name, type_value, class_value, ttl, rdata))
        return self
    

    def additional(self, name, type_value, class_value, ttl, rdata):
        self.__dns_message.additional.rrformat_list.append(self.__build_rrformat(name, type_value, class_value, ttl, rdata))
        return self


    def build(self) -> DnsMessage:
        return self.__dns_message
    

# class DnsMessageBuilder():

#     def __init__(self):
#         self.__dns_message = DnsMessage()

    
#     def enable_rd(self):
#         self.__dns_message.header.rd = True
#         return self
    

#     def enable_ra(self, ra_flag:bool):
#         self.__dns_message.header.ra = True
#         return self
    

#     def set_opcode(self, opcode_type:OPCODE_TYPE):
#         try:
#             self.__dns_message.header.opcode = opcode_type
#         except:
#             pass
#         return self


#     def set_message_type(self, query_type:QUERY_TYPE):
#         try:
#             self.__dns_message.header.query_type = query_type
#         except:
#             pass
#         return self
    

#     def set_id(self,id:int):
#         self.__dns_message.header.id = id

    
#     def set_rcode(self,rcode_type:RCODE_TYPE):
#         try:
#             self.__dns_message.header.rcode = rcode_type
#         except:
#             pass
#         return self
    

#     def enbale_aa(self, aa_flag:bool):
#         self.__dns_message.header.aa = True
#         return self
    
    
#     def set_question(self, domain_name:str, qtype:str, qclass:str):
#         try:
#             self.__dns_message.question.qname  = domain_name
#             self.__dns_message.question.qtype  = QTYPE_VALUES[qtype]
#             self.__dns_message.question.qclass = QCLASS_VALUES[qclass]
#             self.__dns_message.header.qdcount = 1
#         except Exception as e:
#             print(e)
#         return self

#     def build(self) -> DnsMessage:
#         return self.__dns_message

    

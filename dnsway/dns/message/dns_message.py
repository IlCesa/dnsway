# from __future__ import annotations
from __future__ import annotations
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.resource import ResourceRecordMessage
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


class DnsMessageBuilder():

    def __init__(self):
        self.__dns_message = DnsMessage()

    
    def enable_rd(self):
        self.__dns_message.header.set_rd(True)
        return self
    

    def enable_ra(self, ra_flag:bool):
        self.__dns_message.header.set_ra(True)
        return self
    

    def set_opcode(self, opcode_type:OPCODE_TYPE):
        try:
            self.__dns_message.header.set_opcode(opcode_type)
        except:
            pass
        return self


    def set_message_type(self, query_type:QUERY_TYPE):
        try:
            self.__dns_message.header.set_query_type(query_type)
        except:
            pass
        return self
    

    def set_id(self,id:int):
        self.__dns_message.header.id = id

    
    def set_rcode(self,rcode_type:RCODE_TYPE):
        try:
            self.__dns_message.header.set_rcode(rcode_type)
        except:
            pass
        return self
    

    def enbale_aa(self, aa_flag:bool):
        self.__dns_message.header.set_aa(True)
        return self
    
    
    def set_question(self, domain_name:str, qtype:str, qclass:str):
        try:
            self.__dns_message.question.qname  = domain_name
            self.__dns_message.question.qtype  = QTYPE_VALUES[qtype]
            self.__dns_message.question.qclass = QCLASS_VALUES[qclass]
            self.__dns_message.header.qdcount = 1
        except Exception as e:
            print(e)
        return self

    def build(self) -> DnsMessage:
        return self.__dns_message

    

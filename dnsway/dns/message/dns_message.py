# from __future__ import annotations
from __future__ import annotations
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.resource import ResourceRecordMessage
from dnsway.dns.message.question import QuestionMessage
from dnsway.dns.message.header import HeaderMessage

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


    def addHeader(self, header) -> DnsMessageBuilder:
        return self
    
    
    def setSize(self):
        pass


    def setTransport(self):
        pass


    def build(self) -> DnsMessage:
        return self.__dns_message

    

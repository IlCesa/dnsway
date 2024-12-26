from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.resource import ResourceRecordMessage
from dnsway.dns.message.question import QuestionMessage
from dnsway.dns.message.header import HeaderMessage


class DnsMessage(DnsWaySerializer):

    def __init__(self):
        self.header     : HeaderMessage          =  HeaderMessage()
        self.question   : QuestionMessage        =  QuestionMessage()
        self.answer     : ResourceRecordMessage  =  ResourceRecordMessage(label='Answer')
        self.autorithy  : ResourceRecordMessage  =  ResourceRecordMessage(label='Autorithy')
        self.additional : ResourceRecordMessage  =  ResourceRecordMessage(label='Additional')
        
        super().__init__(label = 'DnsMessage')


    def encode(self, /) -> bytearray:
        return super().encode(self.header, self.question, self.answer, self.autorithy, self.additional)

from dnsway.dns.converter.interface import DnsWaySerializer
from dnsway.dns.message.header.header_message import HeaderMessage
from dnsway.dns.message.question.question_message import QuestionMessage
from dnsway.dns.message.resource.rrformat import ResourceRecordFormat


class DnsMessage(DnsWaySerializer):


    def __init__(self):
        self.header:HeaderMessage = HeaderMessage()
        self.question:QuestionMessage = QuestionMessage()
        self.answer:ResourceRecordFormat = ResourceRecordFormat()
        self.autorithy:ResourceRecordFormat = ResourceRecordFormat()
        self.additional:ResourceRecordFormat = ResourceRecordFormat()


    def encode(self):
        return super().encode()
    

    def decode(self, dns_stream):
        return super().decode(dns_stream)

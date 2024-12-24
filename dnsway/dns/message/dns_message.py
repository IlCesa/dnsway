

from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.header import HeaderMessage
from dnsway.dns.message.question import QuestionMessage
from dnsway.dns.message.resource import ResourceRecordFormat


class DnsMessage(DnsWaySerializer):


    def __init__(self):
        self.header:HeaderMessage               = HeaderMessage()
        self.question:QuestionMessage           = QuestionMessage()
        self.answer:ResourceRecordFormat        = ResourceRecordFormat()
        self.autorithy:ResourceRecordFormat     = ResourceRecordFormat()
        self.additional:ResourceRecordFormat    = ResourceRecordFormat()



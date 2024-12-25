from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.resource import ResourceRecordMessage
from dnsway.dns.message.question import QuestionMessage
from dnsway.dns.message.header import HeaderMessage


class DnsMessage(DnsWaySerializer):

    def __init__(self):
        self.header     : HeaderMessage          = HeaderMessage()
        self.question   : QuestionMessage        = QuestionMessage()
        self.answer     : ResourceRecordMessage  = ResourceRecordMessage()
        self.autorithy  : ResourceRecordMessage  = ResourceRecordMessage()
        self.additional : ResourceRecordMessage  = ResourceRecordMessage()

        
        # super.__init__([self.header, self.question, self.answer, self.autorithy, self.additional])

    

    def encode(self, /) -> bytearray : 
        dns_message_list = [self.header, self.question,self.answer,self.autorithy,self.additional]
        encoded_dns_message = bytearray()
        for section in dns_message_list:
            encoded_dns_message = encoded_dns_message + section.encode()

        return encoded_dns_message
    
    
    # def decode(self, msg_byte_stream):
    #     return super().decode(msg_byte_stream)
    
    def dump_message(self):
        for section in [self.header, self.question, self.answer, self.autorithy, self.additional]:
            section.dump_message()


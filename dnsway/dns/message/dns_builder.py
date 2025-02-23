from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.exception import DnsWayMultipleQuestionNotSupported
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.resource import ResourceRecordFormat


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
        
        self.__dns_message.question.qname = qname
        self.__dns_message.question.qtype =  QTYPE_VALUES[qtype] if type(qtype) == str else qtype
        self.__dns_message.question.qclass = QCLASS_VALUES[qclass] if type(qclass) == str else qclass
        self.__dns_message.header.qdcount = 1

        return self


    def answer(self, name, type_value, class_value, ttl, rdata):
        self.__dns_message.header.ancount = self.__dns_message.header.ancount.value+1
        self.__dns_message.answer.rrformat_list.append(self.__build_rrformat(name, type_value, class_value, ttl, rdata))
        return self


    def autorithy(self, name, type_value, class_value, ttl, rdata=None):
        self.__dns_message.header.nscount = self.__dns_message.header.nscount.value+1
        self.__dns_message.autorithy.rrformat_list.append(self.__build_rrformat(name, type_value, class_value, ttl, rdata))
        return self
    

    def additional(self, name, type_value, class_value, ttl, rdata):
        self.__dns_message.header.arcount = self.__dns_message.header.arcount.value+1
        self.__dns_message.additional.rrformat_list.append(self.__build_rrformat(name, type_value, class_value, ttl, rdata))
        return self
    

    # def answer(self, rrformat:ResourceRecordFormat):
    #     self.__dns_message.header.ancount = self.__dns_message.header.ancount.value+1
    #     self.__dns_message.answer.rrformat_list.append(rrformat)
    #     return self


    # def autorithy(self, rrformat:ResourceRecordFormat):
    #     self.__dns_message.header.nscount = self.__dns_message.header.nscount.value+1
    #     self.__dns_message.autorithy.rrformat_list.append(rrformat)
    #     return self
    

    # def additional(self, rrformat:ResourceRecordFormat):
    #     self.__dns_message.header.arcount = self.__dns_message.header.arcount.value+1
    #     self.__dns_message.additional.rrformat_list.append(rrformat)
    #     return self


    def build(self) -> DnsMessage:
        return self.__dns_message


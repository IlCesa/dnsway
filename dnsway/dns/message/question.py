from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer


class QuestionMessage(DnsWaySerializer):

    def __init__(self):
        self.__qname  : DomainName       =   DomainName()
        self.__qtype  : QTYPE_VALUES     =   0x00 
        self.__qclass : QCLASS_VALUES    =   0x00


    @property
    def qname(self):
        return self.__qname
    

    @property
    def qtype(self):
        return self.__qtype
    

    @property
    def qclass(self):
        return self.__qclass
    
    
    @qname.setter
    def qname(self, domain_name:str):
        self.qname.domain_name = domain_name


    @qtype.setter
    def qtype(self, qtype:QTYPE_VALUES):
        self.__qtype = qtype.value & 0xFF


    @qclass.setter
    def qclass(self, qclass:QCLASS_VALUES):
        self.__qclass = qclass.value & 0xFF


    def decode(self, msg_byte_stream:bytes, /) : 
        pass


    def dump_message(self, /) -> None : 
        bits_list = [f"0b{bin(byte)[2:].zfill(8)}" for byte in self.qname.encode()]
        print(f"QNAME   : {bits_list}")
        print(f"QTYPE   : {self.qtype:016b}")
        print(f"QCLASS  : {self.qclass:016b}")

    def encode(self, /) -> bytearray : 
        rrformat_bytes_list = bytearray()
        rrformat_bytes_list = rrformat_bytes_list + self.qname.encode()

        question_message_16bit_list = [
            self.qtype,
            self.qclass,
        ]

        for rrformat_16bit in question_message_16bit_list:
            rrformat_bytes_list = rrformat_bytes_list + rrformat_16bit.to_bytes(length=2,byteorder='big')

        
        return rrformat_bytes_list

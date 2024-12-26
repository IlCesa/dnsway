from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.type import int16


class QuestionMessage(DnsWaySerializer):

    def __init__(self):
        self.__qname  : DomainName  =   DomainName()
        self.__qtype  : int16       =   int16()
        self.__qclass : int16       =   int16()
        
        super().__init__(label='QuestionMessage')


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
        self.__qtype.value = qtype.value


    @qclass.setter
    def qclass(self, qclass:QCLASS_VALUES):
        self.__qclass.value = qclass.value

    
    def encode(self) -> bytearray :
        return super().encode(self.qname, self.qtype,self.qclass)


    # def dump_message(self, /) -> None : 
    #     bits_list = [f"0b{bin(byte)[2:].zfill(8)}" for byte in self.qname.encode()]
    #     print(f"QNAME   : {bits_list}")
    #     print(f"QTYPE   : {self.qtype:016b}")
    #     print(f"QCLASS  : {self.qclass:016b}")

    
    # def decode(self, msg_byte_stream:bytes, /) : 
    #     pass

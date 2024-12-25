from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES, RRecordData
from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer


# this class implementation is about "answer, Authority and additional section of the dns message format"
class ResourceRecordMessage(DnsWaySerializer):
    def __init__(self):
        self.rrformat_list = [ResourceRecordFormat()]

    def encode(self) -> bytearray:
        rrformat_bytes_list = bytearray()
        for rrformat in self.rrformat_list:
            rrformat_bytes_list = rrformat_bytes_list + rrformat.encode()
        return rrformat_bytes_list
    
    def dump_message(self):
        for rrformat in self.rrformat_list:
            rrformat.dump_message()


class ResourceRecordFormat(DnsWaySerializer):

    def __init__(self) -> None:
        self.__name         : DomainName        = DomainName()  # rfc1035 domain name space definition
        self.__type_value   : QTYPE_VALUES      = 0x00          # rr format type
        self.__class_value  : QCLASS_VALUES     = 0x00          # rr format class
        self.__ttl          : int               = 0x00          # unsigned 32 bit value, represent the maximum cachable time of the resource
        self.__rdata_length : int               = 0x00          # represent the length (in octets) of rdata section
        self.__rdata        : RRecordData       = RRecordData() # rdata class object


    @property
    def name(self):
        return self.__name


    @property
    def type_value(self):
        return self.__type_value


    @property
    def class_value(self):
        return self.__class_value
    

    @property
    def ttl(self):
        return self.__ttl
    

    @property
    def rdata_length(self):
        return self.__rdata_length
    

    @property
    def rdata(self):
        return self.__rdata
    

    @name.setter
    def name(self, name):
        # self.__name = domain_name_to_bytes_definition(name)
        pass


    @type_value.setter
    def type_value(self, qtype:QTYPE_VALUES) -> None:
        self.__type_value = qtype


    @class_value.setter
    def class_value(self, qclass:QCLASS_VALUES) -> None:
        self.__class_value = qclass

    
    @ttl.setter
    def ttl(self, ttl:int) -> None:
        self.__ttl = ttl

    @rdata.setter
    def rdata(self) -> None:
        self.rdata = None
        self.rdata_length = self.rdata.byte_length()

    
    def decode(self, msg_byte_stream):
        return super().decode(msg_byte_stream)
    
    
    def dump_message(self):
        bits_list = [f"0b{bin(byte)[2:].zfill(8)}" for byte in self.name.encode()]
        print(f"NAME            : {bits_list}")
        print(f"TYPE            : {self.type_value:016b}")
        print(f"CLASS           : {self.class_value:016b}")
        print(f"TTL             : {self.ttl:032b}")
        print(f"RDATA LENGTH    : {self.ttl:032b}")
        self.rdata.dump_message()


    def encode(self, /) -> bytearray : 
        rrformat_bytes_list = bytearray()
        rrformat_bytes_list = rrformat_bytes_list + self.name.encode()

        rrformat_16bit_list = [
            self.type_value,
            self.class_value,
            self.ttl,
            self.rdata_length
        ]

        for rrformat_16bit in rrformat_16bit_list:
            rrformat_bytes_list = rrformat_bytes_list + rrformat_16bit.to_bytes(length=2,byteorder='big')

        rrformat_bytes_list = rrformat_bytes_list + self.rdata.encode()
        
        return rrformat_bytes_list


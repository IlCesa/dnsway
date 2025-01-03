from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES, RRecordData
from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.type import int16, int32


class ResourceRecordMessage(DnsWaySerializer):

    def __init__(self, label):
        self.rrformat_list = [ResourceRecordFormat()]
        super().__init__(label=f'RRMessage - {label}')


    def encode(self) -> bytearray:
        return super().encode(*self.rrformat_list)



class ResourceRecordFormat(DnsWaySerializer):

    def __init__(self) -> None:
        self.__name         :   DomainName    =     DomainName()        # rfc1035 domain name space definition
        self.__type_value   :   int16         =     int16()             # rr format type
        self.__class_value  :   int16         =     int16()             # rr format class
        self.__ttl          :   int32         =     int32()             # unsigned 32 bit value, represent the maximum cachable time of the resource
        self.__rdata_length :   int16         =     int16()             # represent the length (in octets) of rdata section
        self.__rdata        :   RRecordData   =     RRecordData()       # rdata class object

        super().__init__(label='ResourceRecordFormat')


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
    def name(self, domain_name):
        self.name.domain_name = domain_name


    @type_value.setter
    def type_value(self, qtype:QTYPE_VALUES) -> None:
        self.__type_value.value = qtype.value


    @class_value.setter
    def class_value(self, qclass:QCLASS_VALUES) -> None:
        self.__class_value.value = qclass.value

    
    @ttl.setter
    def ttl(self, ttl:int) -> None:
        self.__ttl.value = ttl


    @rdata.setter
    def rdata(self) -> None:
        self.rdata = None
        self.rdata_length.value = self.rdata.byte_length()


    def encode(self, /) -> bytearray:
        return super().encode(self.name, self.type_value, self.class_value, self.ttl, self.rdata_length, self.rdata)

    
    # def decode(self, msg_byte_stream):
    #     return super().decode(msg_byte_stream)

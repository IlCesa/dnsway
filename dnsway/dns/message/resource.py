from __future__ import annotations
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES, RRecordData
from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.type import int16, int32


class ResourceRecordMessage(DnsWaySerializer):

    def __init__(self, count:int16, label):
        self.count = count
        self.__rrformat_list = []
        super().__init__(label=f'RRMessage - {label}')


    @property
    def rrformat_list(self) -> list:
        return self.__rrformat_list
    

    # @rrformat_list.setter
    # def rrfomat_list(self, rrformat:ResourceRecordFormat):
    #     self.rrformat_list.append(rrformat)


    def encode(self) -> bytearray:
        return super().encode(*self.rrformat_list)
    

    def decode(self, data:bytearray, offset:int) -> int:
        self.__rrformat_list = [ResourceRecordFormat() for _ in range(self.count.value)]
        # print(f"In ResourceRecordMessage decode. Length: {len(self.rrformat_list)}")
        return super().decode(data, offset, *self.rrformat_list)


class ResourceRecordFormat(DnsWaySerializer):

    def __init__(self) -> None:
        self.__name         :   DomainName    =     DomainName()        # rfc1035 domain name space definition
        self.__type_value   :   int16         =     int16()             # rr format type
        self.__class_value  :   int16         =     int16()             # rr format class
        self.__ttl          :   int32         =     int32()             # unsigned 32 bit value, represent the maximum cachable time of the resource
        self.__rdata_length :   int16         =     int16()             # represent the length (in octets) of rdata section
        self.__rdata        :   RRecordData   =     RRecordData(type_value=self.type_value, class_value=self.class_value, rdata_length=self.rdata_length, label='RRecordData')       # rdata class object

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
        self.__name.domain_name = domain_name


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
    def rdata(self, resource_record) -> None:
        self.__rdata.resource_record = resource_record
        self.__rdata_length.value = len(self.rdata.encode())

    
    @rdata_length.setter
    def rdata_length(self, rdata_length:int):
        self.rdata_length.value = rdata_length


    def encode(self, /) -> bytearray:
        return super().encode(self.name, self.type_value, self.class_value, self.ttl, self.rdata_length, self.rdata)
    

    def decode(self, data:bytearray, offset:int, /) -> int:
        k =  super().decode(data, offset, self.name, self.type_value, self.class_value, self.ttl, self.rdata_length, self.rdata)
        # print("RESOURCE DECODED")
        # print("domain name:",self.name.domain_name)
        # print("TTL: ", self.ttl.value)
        return k
    
    
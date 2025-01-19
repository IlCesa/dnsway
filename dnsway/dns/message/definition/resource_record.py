from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from enum import Enum

from dnsway.dns.message.type import int16


class QTYPE_VALUES(Enum):

    A               =   0x1     # a host address
    NS              =   0x2     # an authoritative name server
    MD              =   0x3     # a mail destination (Obsolete - use MX)
    MF              =   0x4     # a mail forwarder (Obsolete - use MX)
    CNAME           =   0x5     # the canonical name for an alias
    SOA             =   0x6     # marks the start of a zone of authority
    MB              =   0x7     # a mailbox domain name (EXPERIMENTAL)
    MG              =   0x8     # a mail group member (EXPERIMENTAL)
    MR              =   0x9     # a mail rename domain name (EXPERIMENTAL)
    NULL            =   0xA     # a null RR (EXPERIMENTAL)
    WKS             =   0xB     # a well known service description
    PTR             =   0xC     # a domain name pointer
    HINFO           =   0xD     # host information
    MINFO           =   0xE     # mailbox or mail list information
    MX              =   0xF     # mail exchange
    TXT             =   0x10    # text strings
    AAAA            =   0x1C    # ipv6 host address
    AXFR            =   0xFC    # A request for a transfer of an entire zone
    MAILB           =   0xFD    # A request for mailbox-related records (MB, MG or MR)
    MAILA           =   0xFE    # A request for mail agent RRs (Obsolete - see MX)
    ALL             =   0xFF    # A request for all records


class QCLASS_VALUES(Enum):
    
    IN              =   0x1     # the Internet
    CS              =   0x2     # the CSNET class (Obsolete - used only for examples in some obsolete RFCs)
    CH              =   0x3     # the CHAOS class
    HS              =   0x4     # Hesiod [Dyer 87]
    ALL             =   0xFF    # any class


#################################
#      ARPA INTERNET RRs        #
#################################


class RRecordData(DnsWaySerializer):

    def __init__(self, type_value:int16, class_value:int16, rdata_length:int16, label):
        self.type_value = type_value
        self.class_value = class_value
        self.rdata_length = rdata_length
        self.resource_record = None

        super().__init__(label)
    

    def encode(self):
        return bytearray() if self.resource_record is None else self.resource_record.encode()

    
    def decode(self, data:bytearray, offset:int) -> int:
        #original_data = bytearray(data)
        #data = data[offset:]
        # print("owndata:",data)
        # print("IN RRECORD DATA DECODE PHASE")
        # print("rdata length",self.rdata_length)
        # print("RRRECORDDATA: ",data)
        # print("------------")
        if len(data) == 0: return 0

        try:
            type_value = QTYPE_VALUES(self.type_value.value)
            class_value = QCLASS_VALUES(self.class_value.value)
        except ValueError:
            print(f"error:{self.type_value.value},{self.class_value.value}")
            #TODO: raise specific error here
            return 0 #for now
        
        if type_value == QTYPE_VALUES.A:
            self.resource_record = ARecord()
        elif type_value == QTYPE_VALUES.AAAA:
            self.resource_record = AAAARecord()
        elif type_value == QTYPE_VALUES.CNAME:
            self.resource_record = CNameRecord()
        elif type_value == QTYPE_VALUES.NS:
            self.resource_record = NSRecord()
        else:
            print(type_value)
            raise Exception("QTYPE NOT SUPPORTED YET.")
        
        self.resource_record.decode(data,offset) 

        return self.rdata_length.value


class WKSRecord():
    pass


class ARecord(DnsWaySerializer):
    
    def __init__(self):
        self.__ip_address = bytearray([0x00,0x00,0x00,0x00])


    @property
    def ip_address(self):
        return self.__ip_address


    @ip_address.setter
    def ip_address(self, ip_address:str):
        ip_decimal_list = ip_address.split('.')
        for ip_decimal,i in enumerate(ip_decimal_list):
            self.ip_address[i] = int(ip_decimal)


    def encode(self, /) -> bytearray:
        return self.ip_address
    

    def decode(self, data:bytearray,offset:int):
        data = bytearray(data[offset:])
        ip_str = ''
        for k in range(0,4):
            octet = data.pop(0)
            ip_str = ip_str + f"{octet}."
            self.ip_address[k] = octet
        ip_str = ip_str[:-1]
        print(ip_str)
        return 4


    def __str__(self) -> str:
        return self.ip_address.__str__()
    

class AAAARecord(DnsWaySerializer):
    
    def __init__(self):
        self.__ipv6_address = bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
    

    @property
    def ipv6_address(self):
        return self.__ipv6_address


    @ipv6_address.setter
    def ip_address(self, ip_address:str):
        ip_decimal_list = ip_address.split(':')
        for ip_decimal,i in enumerate(ip_decimal_list):
            self.ipv6_address[i] = int(ip_decimal)
    

    def encode(self, /) -> bytearray:
        return self.ipv6_address
    

    def decode(self, data:bytearray,offset:int):
        data = bytearray(data[offset:])
        ip_str = ''
        for k in range(0,16,2):
            block = int.from_bytes(data[k:k+1],byteorder='big')
            ip_str = ip_str + f"{hex(block)[2:]}:"
            self.ipv6_address[k] = data[k]
            self.ip_address[k+1] = data[k+1]
        
        ip_str = ip_str[:-1]
        print(ip_str)
        return 16


    def __str__(self) -> str:
        return self.ip_address.__str__()
    


#################################
#        STANDARD RDATA         #
#################################


class CNameRecord(DnsWaySerializer):
    def __init__(self):
        self.__alias_name = DomainName()
    

    @property
    def alias_name(self):
        return self.__alias_name
    

    @alias_name.setter
    def alias_name(self, name: str):
        self.__alias_name.domain_name = name


    def encode(self, /):
        return self.alias_name.encode()
    

    def decode(self, data, offset):
        # print("in decode cname")
        k =  self.alias_name.decode(data, offset)
        # print(self.alias_name.domain_name)
        return k 


class HInfoRecord():
    pass


class MXRecord():
    pass


class NSRecord(DnsWaySerializer):
    def __init__(self):
        self.__alias_name = DomainName()
    

    @property
    def alias_name(self):
        return self.__alias_name
    

    @alias_name.setter
    def alias_name(self, name: str):
        self.__alias_name.domain_name = name


    def encode(self, /):
        return self.alias_name.encode()
    

    def decode(self, data, offset):
        k =  self.alias_name.decode(data, offset)
        return k 


class PTRRecord():
    pass


class SOARecord():
    pass


class TXTRecord():
    pass


#################################
#      EXPERIMENTAL RDATA       #
#################################


class MBRecord():
    pass


class MGRecord():
    pass


class MInfoRecord():
    pass


class MRRecord():
    pass


class NullRecord():
    pass


#################################
#           OBSOLETE            #
#################################


class MDRecord():
    pass


class MFRecord():
    pass

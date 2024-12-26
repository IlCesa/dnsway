from dnsway.dns.message.dns_serialize import DnsWaySerializer
from enum import Enum


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
    
    def encode(self):
        return bytearray()


    def dump_message(self):
        pass


class WKSRecord():
    pass


class ARecord(RRecordData):
    
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
    
    def dump_message(self):
        bits_list = [f"0b{bin(byte)[2:].zfill(8)}" for byte in self.encode()]
        print(f"IPADDRESS   : {bits_list}")


    def byte_length(self, /) -> int:
        return len(self.encode())


    def __str__(self):
        return self.ip_address.__str__()


#################################
#        STANDARD RDATA         #
#################################


class CNameRecord():
    def __init__(self, alias_name:str):
        self.alias_name = bytearray([0x00,0x00,0x00,0x00])
        self.set_alias_name(alias_name)
    

    def set_alias_name(self, alias_name:str) -> None:
        pass
        #self.alias_name = domain_name_to_bytes_definition(alias_name)


class HInfoRecord():
    pass


class MXRecord():
    pass


class NSRecord():
    pass


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

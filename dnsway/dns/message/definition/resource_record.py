import time
from dnsway.dns.message.definition.domain_name import DomainName
from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.type import int16, int32
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
        self.__resource_record = None

        super().__init__(label)


    @property
    def resource_record(self):
        return self.__resource_record
    
    
    @resource_record.setter
    def resource_record(self, resource_record):
        self.__resource_record = resource_record
    

    def encode(self):
        if self.resource_record is None:
            return bytearray()
        else:
            return self.resource_record.encode()
            #rr_encoded = self.resource_record.encode()
            # print("cname len",len(rr_encoded))
            # self.rdata_length = len(rr_encoded)
            #return rr_encoded

    
    def decode(self, data:bytearray, offset:int) -> int:
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
        elif type_value == QTYPE_VALUES.SOA:
            self.resource_record = SOARecord()
        elif type_value == QTYPE_VALUES.MX:
            self.resource_record = MXRecord()
        elif type_value == QTYPE_VALUES.PTR:
            self.resource_record = PTRRecord()
        elif type_value == QTYPE_VALUES.TXT:
            data = bytearray(data[offset:offset+self.rdata_length.value])
            self.resource_record = TXTRecord()
        else:
            print(type_value)
            raise Exception("QTYPE NOT SUPPORTED YET.")
        
        return self.resource_record.decode(data,offset) 

        #return self.rdata_length.value


class WKSRecord():
    pass


class ARecord(DnsWaySerializer):
    
    def __init__(self):
        self.__ip_address = bytearray([0x00,0x00,0x00,0x00])
        self.__ip_address_str = ''


    @property
    def ip_address(self):
        return self.__ip_address


    @ip_address.setter
    def ip_address(self, ip_address:str):
        ip_decimal_list = ip_address.split('.')
        # print(ip_decimal_list)
        for i,ip_decimal in enumerate(ip_decimal_list):
            self.ip_address[i] = int(ip_decimal)
            # print(i,int(ip_decimal))

        self.__ip_address_str = ip_address
        
       # time.sleep(100)

    


    def encode(self, /) -> bytearray:

        return self.ip_address
    

    # def __bytes_to_str(self, data:bytes):
    #     ip_str = ''
    #     for k in range(0,4):
    #         octet = data.pop(0)
    #         ip_str = ip_str + f"{octet}."
    #         self.ip_address[k] = octet
    #     ip_str = ip_str[:-1]
    #     self.__ip_address_str = ip_str
    

    def decode(self, data:bytearray,offset:int):
        data = bytearray(data[offset:])
        ip_str = ''
        for k in range(0,4):
            octet = data.pop(0)
            ip_str = ip_str + f"{octet}."
            self.ip_address[k] = octet
        ip_str = ip_str[:-1]
        self.__ip_address_str = ip_str
        # print(ip_str)
        return 4


    def __str__(self) -> str:
        return self.__ip_address_str
    

class AAAARecord(DnsWaySerializer):
    
    def __init__(self):
        self.__ipv6_address = bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
        self.__ipv6_address_str = ''

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
        self.__ipv6_address_str = ip_str
        # print(ip_str)
        return 16


    def __str__(self) -> str:
        return self.__ipv6_address_str.__str__()
    

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
        return self.alias_name.decode(data, offset)
        # k =  self.alias_name.decode(data, offset)
        # # print(self.alias_name.domain_name)
        # return k 
    
    def __str__(self):
        return self.alias_name.domain_name


class HInfoRecord():
    pass


class MXRecord(DnsWaySerializer):
    def __init__(self):
        self.__preference = int16()
        self.__exchange = DomainName()

    @property
    def preference(self):
        return self.__preference
    
    @property
    def exchange(self):
        return self.__exchange
    
    @preference.setter
    def preference(self, value:int):
        self.__preference.value = value

    @exchange.setter
    def exchange(self, domain_name:str):
        self.__exchange.domain_name = domain_name
    
    def encode(self):
        return super().encode(self.preference, self.exchange)
    
    def decode(self, data, offset):
        return super().decode(data, offset, self.preference, self.exchange)

    


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
        return self.alias_name.decode(data, offset)
    
    def __str__(self):
        return self.alias_name.domain_name


class PTRRecord(DnsWaySerializer):
    def __init__(self):
        self.__ptrdname = DomainName()

    @property
    def ptrdname(self):
        return self.__ptrdname
    
    @ptrdname.setter
    def ptrdname(self, domain_name:str):
        self.__ptrdname.domain_name = domain_name

    def encode(self, *args):
        return super().encode(self.ptrdname)
    
    def decode(self, data, offset, *args):
        return super().decode(data, offset, self.ptrdname)


class SOARecord(DnsWaySerializer):
    def __init__(self):
        self.__mname    =     DomainName()
        self.__rname    =     DomainName()
        self.__serial   =     int32()
        self.__refresh  =     int32()
        self.__retry    =     int32()
        self.__expire   =     int32()
        self.__minimum  =     int32()
    
    @property
    def mname(self):
        return self.__mname
    
    @property
    def rname(self):
        return self.__rname
    
    @property
    def serial(self):
        return self.__serial
    
    @property
    def refresh(self):
        return self.__refresh
    
    @property
    def retry(self):
        return self.__retry
    
    @property
    def expire(self):
        return self.__expire
    
    @property
    def minimum(self):
        return self.__minimum

    @mname.setter
    def mname(self,mname:str):
        self.__mname.domain_name = mname

    @rname.setter
    def rname(self,rname:str):
        self.__rname.domain_name = rname

    @serial.setter
    def serial(self,serial:int):
        self.__serial.value = serial

    @refresh.setter
    def refresh(self,refresh:int):
        self.__refresh.value = refresh

    @retry.setter
    def retry(self,retry:int):
        self.__retry.value = retry

    @expire.setter
    def expire(self,expire:int):
        self.__expire.value = expire

    @minimum.setter
    def minimum(self,minimum:int):
        self.__minimum.value = minimum

    def encode(self, /):
        return super().encode(self.mname, self.rname, self.serial, self.refresh, self.retry, self.expire, self.minimum)

    def decode(self, data, offset):
        return super().decode(data, offset, self.mname, self.rname, self.serial, self.refresh, self.retry, self.expire, self.minimum)
    
    def __str__(self):
        return f"{self.mname.domain_name} {self.rname.domain_name} {self.serial} {self.refresh} {self.retry} {self.expire} {self.minimum}"


class TXTRecord(DnsWaySerializer):
    def __init__(self):
        self.__txt_data = ''

    @property
    def txt_data(self):
        return self.__txt_data
    
    @txt_data.setter
    def txt_data(self, data:str):
        self.__txt_data = data
    
    def encode(self):
        # qui dovrei dividere ogni 256 byte, per ora mennefottoMeloo (viva u pilu) PS: a chi cazz i serve a LAUUUREA
        str_byte =  len(self.txt_data).to_bytes(1, 'big')  + self.txt_data.encode('utf-8')
        return str_byte
    
    def decode(self, data:bytearray, offset):
        rtn_val = len(data)
        while len(data) > 0:
            str_len = data.pop(0)
            byte_str = data[:str_len].decode(encoding='utf-8')
            self.__txt_data += byte_str
            data = data[str_len:]
        return rtn_val


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


from dnsway.dns.message.util import domain_name_to_bytes_definition


#################################
#      ARPA INTERNET RRs        #
#################################


class WKSRecord():
    pass


class ARecord():
    def __init__(self, ip_address:str):
        self.ip_address = bytearray([0x00,0x00,0x00,0x00])
        self.set_ip_address(ip_address)


    def set_ip_address(self, ip_address:str):
        ip_decimal_list = ip_address.split('.')
        for ip_decimal,i in enumerate(ip_decimal_list):
            self.ip_address[i] = int(ip_decimal)


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
        self.alias_name = domain_name_to_bytes_definition(alias_name)


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

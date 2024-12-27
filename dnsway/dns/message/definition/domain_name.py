from dnsway.dns.message.dns_serialize import DnsWaySerializer


class DomainName(DnsWaySerializer):
    def __init__(self):
        self.__domain_name:str = ''

        super().__init__(label='DomainName')


    @property
    def domain_name(self):
        return self.__domain_name
    

    @domain_name.setter
    def domain_name(self, domain_name:str):
        self.__domain_name = domain_name

    
    def encode(self) -> bytearray:
        qname = bytearray()
        subdomain_list = self.domain_name.split('.')
        for subdomain in subdomain_list:
            length_octet = len(subdomain) & 0x3F # mask to extract 6 bit only
            qname.append(length_octet)
            for subdomain_char in subdomain:
                single_char = ord(subdomain_char) & 0xFF # mask to extract 8 bit only
                qname.append(single_char)
        qname.append(0x00) #adding zero null octet
        return qname
    
    def decode(self, msg_byte_stream):
        return super().decode(msg_byte_stream)

from dnsway.dns.message.dns_serialize import DnsWaySerializer


class DomainName(DnsWaySerializer):
    def __init__(self):
        self.__domain_name = 0x00


    @property
    def domain_name(self):
        return self.__domain_name
    

    @domain_name.setter
    def domain_name(self, domain_name:str):
        self.__domain_name = domain_name


    # TODO: prevedere un meccanismo di compressione del messaggio tramite gestione dei puntatori (vedere 4.1.4. Message compression)
    def name_to_bytes(self) -> bytearray:
        qname = bytearray()
        subdomain_list = self.domain_name.split('.')
        for subdomain in subdomain_list:
            length_octet = len(subdomain) & 0x3F # maschera per prendere solo i primi 6 bit
            qname.append(length_octet)
            for subdomain_char in subdomain:
                single_char = ord(subdomain_char) & 0xFF # maschera per estrarre 8 bit
                qname.append(single_char)
        qname.append(0x00) #adding zero null octet
        return qname
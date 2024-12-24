from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_serialize import DnsWaySerializer


class QuestionMessage(DnsWaySerializer):
    def __init__(self):
        self.qname = bytearray([0x00,0x00])
        self.qtype = 0x00
        self.qclass = 0x00

    #TODO: 
        #1) contiene punti?
        #2) ogni label ha una struttura corretta?
        #per ora assumiamo di si.
        # "3 www" -> "6 google" -> "2 it" -> "000000"
        #prevedere un meccanismo di compressione del messaggio tramite gestione dei puntatori (vedere 4.1.4. Message compression)

    def set_qname(self, domain_name:str):
        subdomain_list = domain_name.split('.')
        for subdomain in subdomain_list:
            length_octet = len(subdomain) & 0x3F #maschera per prendere solo i primi 6 bit
            self.qname.append(length_octet)
            for subdomain_char in subdomain:
                letter = ord(subdomain_char) & 0xFF #maschera per estrarre 8 bit
                self.qname.append(letter)
        #add zero null octet at the end
        self.qname.append(0x00)


    def set_qtype(self, qtype:QTYPE_VALUES):
        self.qtype = qtype.value & 0xFF


    def set_qclass(self, qclass:QCLASS_VALUES):
        self.qclass = qclass.value & 0xFF

    
    def __str__(self):
        bits_list = [f"0b{bin(byte)[2:].zfill(8)}" for byte in self.qname]
        print(f"QNAME   : {bits_list}")
        print(f"QTYPE   : {self.qtype:016b}")
        print(f"QCLASS  : {self.qclass:016b}")
        return ""

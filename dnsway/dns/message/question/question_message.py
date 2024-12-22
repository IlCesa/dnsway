


from dnsway.dns.converter.interface import DnsInterface
from dnsway.dns.message.resource.rrvalue import QCLASS_VALUES, QTYPE_VALUES


class QuestionMessage(DnsInterface):
    def __init__(self):
        self.qname = bytearray()
        self.qtype = 0x00
        self.qclass = 0x00
    

    def set_qname(self, domain_name:str):
        '''domain name param example: www.google.it'''
        #1) contiene punti?
        #2) ogni label ha una struttura corretta?
        #per ora assumiamo di si.
        # "3 www" -> "6 google" -> "2 it" -> "000000"
        #TODO: prevedere un meccanismo di compressione del messaggio tramite gestione dei puntatori (vedere 4.1.4. Message compression)

        subdomain_list = domain_name.split('.')
        print(f"{subdomain_list}")

        for subdomain in subdomain_list:
            print(f"processing subdomain: {subdomain}")
            subdomain_length = len(subdomain)
            length_octet = subdomain_length & 0x3F #maschera per prendere solo i primi 6 bit
            self.qname.append(length_octet)
            print(f"adding length byte: {self.qname}")

            for subdomain_char in subdomain:
                letter = ord(subdomain_char) & 0xFF #maschera per estrarre 8 bit
                self.qname.append(letter)

        #adding zero null octet as octet qname termination.
        self.qname.append(0x00)
        print(f"qname after full process: {self.qname}")


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


    def msg_to_byte(self):
        pass

    def byte_to_msg(self):
        pass
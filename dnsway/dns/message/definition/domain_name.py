from dnsway.dns.message.dns_serialize import DnsWaySerializer
from copy import deepcopy

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
        qname.append(0x00)
        return qname
    
    
    def decode(self, data:bytearray, offset:int) -> int:
        original_data = bytearray(data)
        data = data[offset:]
        if len(data) == 0: return 0
        
        # print(f"own data: {data}")
        consumed_byte = i = 0
        ptr_found = False
        while data[i] != 0x00:
            is_a_ptr = (data[i] & 0xC0) == 0xC0
            if is_a_ptr:
                if not ptr_found: #se un puntatore è stato gia' trovato non deve incrementare i byte consumati.
                    consumed_byte = consumed_byte + 2
                ptr_found = True
                ptr_byte_index = int.from_bytes(data[i:i+2], byteorder='big') & 0x3FFF
                # print("IS A PTR:",data[i],"byte index:",ptr_byte_index)
                data = original_data[ptr_byte_index:]
                i = 0
            else:
                subdomain_length = data[i]
                if not ptr_found:
                    consumed_byte = consumed_byte + subdomain_length + 1
                for k in range(0,subdomain_length):
                    single_char = data[i+k+1]
                    self.domain_name+=chr(single_char)
                i = i + k + 2
                self.domain_name += '.'                
        if not ptr_found:
            consumed_byte = consumed_byte + 1 # the null octet
        # print("decoded name:",self.domain_name)
        # print("consumed byte:",consumed_byte)
        return consumed_byte

        '''name_bytes = bytearray()
        consumed_byte = 0
        first_octet = data[0]
        if (first_octet & 0xC0) == 0xC0:
            name_offset = first_octet & 0x3F
            data = original_data[name_offset:]'''



        '''for i,_ in enumerate(data):
            name_bytes.append(data[i])
            consumed_byte = consumed_byte + 1
            if data[i] == 0x00: 
                break
            
        while len(name_bytes) > 0:
            subdomain_length = name_bytes.pop(0)
            if subdomain_length != 0x00:
                for _ in range(0, subdomain_length):
                    single_char = name_bytes.pop(0)
                    self.domain_name+=chr(single_char)
                self.domain_name += '.'

        self.domain_name = self.domain_name[:-1]
        print(self.domain_name)

        return consumed_byte'''


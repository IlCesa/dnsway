from dnsway.dns.message.dns_serialize import DnsWaySerializer


class int16(int, DnsWaySerializer):

    def __init__(self, value = 0x0):
        self.value = value
        DnsWaySerializer.__init__(self, label='int16')


    @property
    def value(self) -> int:
        return self.__value

    
    @value.setter
    def value(self, value) -> None:
        self.__value = value & 0xFFFF


    def encode(self):
        return self.value.to_bytes(length=2, byteorder='big')

    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()



class int32(DnsWaySerializer):

    def __init__(self, value = 0x0):
        self.value = value
        DnsWaySerializer.__init__(self, label='int32')


    @property
    def value(self) -> int:
        return self.__value

    
    @value.setter
    def value(self, value) -> None:
        self.__value = value  & 0xFFFFFFFF


    def encode(self) -> bytearray:
        return self.value.to_bytes(length=4, byteorder='big')
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()

    
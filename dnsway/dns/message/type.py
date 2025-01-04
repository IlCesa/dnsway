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


    def encode(self) -> bytearray:
        return self.value.to_bytes(length=2, byteorder='big')
    
    
    def decode(self, data:bytearray, offset:int) -> int:
        data = data[offset:offset+2]
        if len(data) == 0: return 0
        # print(f"bytes to decode: {data}")
        self.value = int.from_bytes(data, byteorder='big')
        return 2


    def __str__(self) -> str:
        return str(self.value)
    
    
    def __repr__(self) -> str:
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
    

    def decode(self, data:bytearray, offset) -> int:
        data = data[offset:offset+4]
        if len(data) == 0: return 0
        # print(f"bytes to decode: {data}")
        self.value = int.from_bytes(data, byteorder='big')
        return 4

    
    def __str__(self) -> str:
        return str(self.value)
    
    
    def __repr__(self) -> str:
        return self.__str__()

    
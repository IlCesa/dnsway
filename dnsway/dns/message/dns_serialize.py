from dnsway.dns.message.exception import DnsWayDumpingNotSupported, DnsWayEncoderNotSupported
from abc import ABC, abstractmethod


class DnsWaySerializer(ABC):
    
    def __init__(self, label = None):
        super().__init__()
        self.label = label


    @abstractmethod
    def encode(self, /) -> None: ...


    # @abstractmethod
    # def decode(self, msg_byte_stream:bytes, /) : ...


    def length(self, /) -> int: 
        return len(self.encode())
            

    def encode(self, *args) -> bytearray :
        enc_bytes = bytearray()
        for obj in args:
            if isinstance(obj, DnsWaySerializer):
                enc_bytes += obj.encode()
            else:
                raise DnsWayEncoderNotSupported(f"Encoding failed in {self.label}: {type(obj)} not supported.")
        return enc_bytes
    

    def hex_dump(self, width=16) -> None :
        self.__hexdump(self.encode(), width)
        

    def __hexdump(self, data: bytearray, width: int = 16):
        for i in range(0, len(data), width):
            address = f"{i:08x}"
            hex_section = " ".join(f"{b:02x}" for b in data[i:i+width])
            padding = "   " * (width - len(data[i:i+width]))
            ascii_section = "".join(chr(b) if 32 <= b <= 126 else '.' for b in data[i:i+width])
            print(f"{address}  {hex_section}{padding}  |{ascii_section}|")
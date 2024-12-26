from dnsway.dns.message.exception import DnsWayEncoderNotSupported
from abc import ABC, abstractmethod


class DnsWaySerializer(ABC):
    
    def __init__(self, label = None):
        super().__init__()
        self.label = label


    @abstractmethod
    def encode(self, /) -> None: ...


    # @abstractmethod
    # def decode(self, msg_byte_stream:bytes, /) : ...


    # @abstractmethod
    # def byte_length(self, /) -> int: return len(self.encode())


    # @abstractmethod
    # def dump_message(self, /) -> None : ...


    def encode(self, *args) -> bytearray :
        enc_bytes = bytearray()
        for obj in args:
            if isinstance(obj, DnsWaySerializer):
                enc_bytes += obj.encode()
            else:
                raise DnsWayEncoderNotSupported(f"Encoding failed in {self.label}: {type(obj)} not supported.")
        return enc_bytes
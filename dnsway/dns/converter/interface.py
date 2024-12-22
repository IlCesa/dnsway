
from abc import ABC, abstractmethod


class DnsWaySerializer(ABC):
    
    @abstractmethod
    def encode(self) -> bytearray:
        pass

    @abstractmethod
    def decode(self, dns_stream:bytes) -> object:
        pass
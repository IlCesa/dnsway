
from abc import ABC, abstractmethod


class DnsWaySerializer(ABC):
    
    def __init__(self):
        super().__init__()
       

    @abstractmethod
    def encode(self, /) -> bytearray : ...

    @abstractmethod
    def decode(self, msg_byte_stream:bytes, /) : ...

    @abstractmethod
    def byte_length(self, /) -> int : ...

    @abstractmethod
    def dump_message(self, /) -> None : ...
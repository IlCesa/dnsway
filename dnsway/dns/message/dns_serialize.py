from abc import ABC, abstractmethod


class DnsWaySerializer(ABC):
    
    def __init__(self, *args):
        super().__init__()
        #check che siano tutti is-a DnsWaySerializer qui
        # aggiungere controllo anche sulla lunghezza, se la lista è vuota significa che il compontente del messaggio non è stato definito correttamente nella subclass
        self.dns_message = args
       
    @abstractmethod
    def encode(self, /) -> bytearray : ...
    #    return bytearray([section.encode for section in self.dns_message])


    # @abstractmethod
    # def decode(self, msg_byte_stream:bytes, /) : ...


    def byte_length(self, /) -> int : 
        return len(self.encode())


    @abstractmethod
    def dump_message(self, /) -> None : ...
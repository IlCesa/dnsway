from dnsway.dns.message.exception import DnsWayDecoderNotSupported, DnsWayDumpingNotSupported, DnsWayEncoderNotSupported
from abc import ABC, abstractmethod


class DnsWaySerializer(ABC):
    
    def __init__(self, label = None) -> None:
        super().__init__()
        self.label = label


    @abstractmethod
    def encode(self, /) -> None: ...

    
    def decode(self, data:bytearray, offset:int, /) -> int: ...


    def decode(self, data:bytearray, offset:int, *args:list) -> int:
        total_byte_consumed = 0
        # TODO: usare bytes con memoryview per questo specifico problema. Questo perche' usando bytearray viene meno il principio del minor privilegio.
        # quindi potenzialmente i metodi di decode di ogni oggetto, che ricevono l'intera sequenza di byte del messaggio, potrebbero modificarne la struttura e questo non deve accadere.
        # ovviamente è uno scenario decisamente improbabile ma resta uno scenario "possibile".
        for obj in args:
            if isinstance(obj, DnsWaySerializer):
                byte_consumed = 0
                try:
                    # print(f"offsett: {offset+total_byte_consumed}")
                    byte_consumed = obj.decode(bytearray(data), offset+total_byte_consumed)
                except Exception as ee:
                    print(f"error in decode {self.label}")
                    print(f"err: {repr(ee)}")
                #data = data[byte_consumed:]
                total_byte_consumed += byte_consumed
            else:
                raise DnsWayDecoderNotSupported(f"Decoding failed in {self.label}: {type(obj)} not supported.")
            
        # TODO: controllare se tutti i byte sono stati consumati
        return total_byte_consumed
        

    def encode(self, *args:list) -> bytearray:
        enc_bytes = bytearray()
        for obj in args:
            if isinstance(obj, DnsWaySerializer):
                enc_bytes += obj.encode()
            else:
                raise DnsWayEncoderNotSupported(f"Encoding failed in {self.label}: {type(obj)} not supported.")
        return enc_bytes
    

    def length(self, /) -> int: 
        return len(self.encode())
    

    def hex_dump(self, width=16) -> None:
        self.__hex_dump(self.encode(), width)
        
    
    def __hex_dump(self, data: bytearray, width: int = 16) -> None:
        for i in range(0, len(data), width):
            address = f"{i:08x}"
            hex_section = " ".join(f"{b:02x}" for b in data[i:i+width])
            padding = "   " * (width - len(data[i:i+width]))
            ascii_section = "".join(chr(b) if 32 <= b <= 126 else '.' for b in data[i:i+width])
            print(f"{address}  {hex_section}{padding}  |{ascii_section}|")


from dnsway.dns.message.dns_serialize import DnsWaySerializer
from dnsway.dns.message.type import int16
from enum import Enum
import random


class QUERY_TYPE(Enum):

    QUERY           =   0x0         # query message
    RESPONSE        =   0x1         # response message


class OPCODE_TYPE(Enum):

    QUERY           =   0x0         # standard query
    IQUERY          =   0x1         # inverse querys
    STATUS          =   0x2         # server status request


class RCODE_TYPE(Enum):

    NO_ERROR        =   0x0         # No error condition
    FORMAT_ERROR    =   0x1         # Format error - The name server was unable to interpret the query.
    SERVER_FAILURE  =   0x2         # Server failure - The name server was unable to process this query due to a problem with the name server.
    NAME_ERROR      =   0x3         # Response only from an autorithative server. The requested domain name does not exists
    NOT_IMPLEMENTED =   0x4         # The name server does not support the requested kind of query.
    REFUSED         =   0x5         # The name server refuses to perform the operation for policy reason. For example the name server may not wish to provide the information.


# -- INFO ABOUT HEADER_FLAGS -- #
# 1 bit QR QUERY TYPE (0 query, 1 response)
# 4 bit OPCODE (0 standard query, 1 inverse query, 2 server status request)
# 1 bit AA (valid only in response, specify that the responding name server the autorithative one)
# 1 bit TC that stands for truncation (if the whole message is > 512bytes the flag should be 1 and we should use a tcp connection instead)
# 1 bit RD recursion desired (nno capito)
# 1 bit RA recursion available (only if server support recursive option)
# 3 bit Z (future use) must be ALL ZEROS
# 4 bit RCODE (part of the response)


class HeaderMessage(DnsWaySerializer):
    
    QUERY_TYPE_SHIFT_BITS   =     15
    OPCODE_SHIFT_BITS       =     11
    AA_SHIFT_BITS           =     10
    TC_SHIFT_BITS           =     9
    RD_SHIFT_BITS           =     8
    RA_SHIFT_BITS           =     7
    RCODE_SHIFT_BITS        =     0
    
    def __init__(self):
        self.__id       :   int16   =   int16(int.from_bytes(random.randbytes(2), byteorder='big'))
        self.__flags    :   int16   =   int16() 
        self.__qdcount  :   int16   =   int16() 
        self.__ancount  :   int16   =   int16() 
        self.__nscount  :   int16   =   int16() 
        self.__arcount  :   int16   =   int16() 
        
        super().__init__(label='HeaderMessage')
    

    @property
    def id(self):
        return self.__id
    

    @property
    def flags(self):
        return self.__flags


    @property
    def qdcount(self):
        return self.__qdcount
    

    @property
    def ancount(self):
        return self.__ancount
    

    @property
    def nscount(self):
        return self.__nscount
    

    @property
    def arcount(self):
        return self.__arcount
    
    # HEADER BLOCK PROPERTIES

    @property
    def query_type(self) -> QUERY_TYPE:
        qr_value = (self.flags.value >> self.QUERY_TYPE_SHIFT_BITS) & 1
        return QUERY_TYPE(qr_value) 


    @property
    def opcode(self):
        opcode_value = (self.flags.value >> self.OPCODE_SHIFT_BITS) & 0xF
        return OPCODE_TYPE(opcode_value) 


    @property
    def aa(self):
        return (self.flags.value >> self.AA_SHIFT_BITS) & 1


    @property
    def tc(self):
        return (self.flags.value >> self.TC_SHIFT_BITS) & 1


    @property
    def rd(self):
        return (self.flags.value >> self.RD_SHIFT_BITS) & 1


    @property
    def ra(self):
        return (self.flags.value >> self.RA_SHIFT_BITS) & 1


    @property
    def rcode(self):
        rcode_value = self.flags.value & 0xF
        return RCODE_TYPE(rcode_value)

    #HEADER BLOCK END

    @id.setter
    def id(self,id:int):
        self.id.value = id


    @query_type.setter
    def query_type(self, query_type:QUERY_TYPE) -> None:
        self.__flags.value = self.__flags.value & 0x7FFF
        if query_type == QUERY_TYPE.RESPONSE:
            self.__flags.value = self.__flags.value | (0x1 << self.QUERY_TYPE_SHIFT_BITS)
    

    @opcode.setter
    def opcode(self, opcode_type:OPCODE_TYPE):
        self.__flags.value = self.__flags.value & 0x87FF
        self.__flags.value = self.__flags.value | (opcode_type.value << self.OPCODE_SHIFT_BITS)


    @aa.setter
    def aa(self, aa_flag:bool):
        self.__flags.value = self.__flags.value & (0xFBFF)
        if aa_flag:
            self.__flags.value = self.__flags.value | (0x1 << self.AA_SHIFT_BITS)
       
            
    @tc.setter
    def tc(self, tc_flag:bool):
        self.__flags.value = self.__flags.value & (0xFDFF)
        if tc_flag:
            self.__flags.value = self.__flags.value | (0x1 << self.TC_SHIFT_BITS)     


    @rd.setter
    def rd(self, rd_flag:bool):
        self.__flags.value = self.__flags.value & (0xFEFF)
        if rd_flag:
            self.__flags.value = self.__flags.value | (0x1 << self.RD_SHIFT_BITS)


    @ra.setter
    def ra(self, ra_flag:bool):
        self.__flags.value = self.__flags.value & (0xFF7F)
        if ra_flag:
            self.__flags.value = self.__flags.value | (0x1 << self.RA_SHIFT_BITS)       


    @rcode.setter
    def rcode(self, rcode_type:RCODE_TYPE):
        self.__flags.value = self.__flags.value & 0xFFF8
        self.__flags.value = self.__flags.value | (rcode_type.value << self.RCODE_SHIFT_BITS)


    @qdcount.setter
    def qdcount(self, query_count:int):
        self.__qdcount.value = query_count


    @ancount.setter
    def ancount(self, answer_count:int):
        self.__ancount.value = answer_count


    @nscount.setter
    def nscount(self, nameserver_count):
        self.__nscount.value = nameserver_count


    @arcount.setter
    def arcount(self, additional_records_count:int):
        self.__arcount.value = additional_records_count

    
    def encode(self) -> bytearray:
        return super().encode(self.id, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount)

    
    def decode(self, data:bytearray, offset:int) -> int:
        return super().decode(data, offset, self.id, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount)
        # k =  super().decode(data, offset, self.id, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount)
        # '''print("answercount:",self.ancount,"-----------")
        # print("QDCOUNT:",self.qdcount,"-----------")
        # print("nscount:",self.nscount,"-----------")
        # print("arcount:",self.arcount,"-----------")
        # print("HEADER DECODED")'''
        # return k


    # def __str__(self):
    #     return str(bin(int.from_bytes(self.encode(),byteorder='big')))
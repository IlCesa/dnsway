from dnsway.dns.message.dns_serialize import DnsWaySerializer
from enum import Enum
import random


class QUERY_TYPE(Enum):
    QUERY           =   0x7FFF  # a query message
    RESPONSE        =   0x8000  # a response message


class OPCODE_TYPE(Enum):
    QUERY           =   0x0 # standard query
    IQUERY          =   0x1 << 11 # inverse querys
    STATUS          =   0x2 << 11 # server status request


class RCODE_TYPE(Enum):
    NO_ERROR        =   0x0     # No error condition
    FORMAT_ERROR    =   0x1     # Format error - The name server was unable to interpret the query.
    SERVER_FAILURE  =   0x2     # Server failure - The name server was unable to process this query due to a problem with the name server.
    NAME_ERROR      =   0x3     # Response only from an autorithative server. The requested domain name does not exists
    NOT_IMPLEMENTED =   0x4     # The name server does not support the requested kind of query.
    REFUSED         =   0x5     # The name server refuses to perform the operation for policy reason. For example the name server may not wish to provide the information.

## INFO ABOUT HEADER_FLAGS ##
# 1 bit QR QUERY TYPE (0 query, 1 response)
# 4 bit OPCODE (0 standard query, 1 inverse query, 2 server status request)
# 1 bit AA (valid only in response, specify that the responding name server the autorithative one)
# 1 bit TC that stands for truncation (if the whole message is > 512bytes the flag should be 1 and we should use a tcp connection instead)
# 1 bit RD recursion desired (nno capito)
# 1 bit RA recursion available (only if server support recursive option)
# 3 bit Z (future use) must be ALL ZEROS
# 4 bit RCODE (part of the response)


class HeaderMessage(DnsWaySerializer):
    
    def __init__(self):
        self.__id             = 0x00
        self.__header_flags   = 0x00 
        self.__qdcount        = 0x00 
        self.__ancount        = 0x00 
        self.__nscount        = 0x00 
        self.__arcount        = 0x00 #int(b'0x00',16)
        #super.__init__(params_list)

            
    @property
    def id(self):
        return self.__id
    

    @property
    def flags(self):
        return self.__header_flags


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

    
    
    def set_random_id(self):
        self.id = random.randbytes(2)


    @id.setter
    def id(self,id:int):
        self.id = id.to_bytes(2,signed=True)


    def set_query_type(self, query_type:QUERY_TYPE) -> None:
        if query_type == QUERY_TYPE.QUERY:
            #print(f"{QUERY_TYPE.QUERY.name}:{hex(QUERY_TYPE.QUERY.value)} ")
            self.header_flags = self.header_flags & query_type.value
        elif query_type == QUERY_TYPE.RESPONSE:
            self.header_flags = self.header_flags | query_type.value
    

    def set_opcode(self, opcode_type:OPCODE_TYPE):
        #clear the opcode bits
        self.header_flags = self.header_flags & 0x87FF
        if opcode_type == OPCODE_TYPE.QUERY:
            self.header_flags = self.header_flags & 0x87FF
        elif opcode_type == OPCODE_TYPE.IQUERY:
            self.header_flags = self.header_flags | (opcode_type.value)
        elif opcode_type == OPCODE_TYPE.STATUS:
            self.header_flags = self.header_flags | opcode_type.value


    def set_aa(self, aa_flag:bool):
        if aa_flag:
            self.header_flags = self.header_flags | (0x1 << 10)
        else:
            self.header_flags = self.header_flags & (0xFBFF)


    def set_tc(self, tc_flag:bool):
        '''
        '''
        if tc_flag:
            self.header_flags = self.header_flags | (0x1 << 9)
        else:
            self.header_flags = self.header_flags & (0xFDFF)


    def set_rd(self, rd_flag:bool):
        if rd_flag:
            self.header_flags = self.header_flags | (0x1 << 8)
        else:
            self.header_flags = self.header_flags & (0xFEFF)


    def set_ra(self, ra_flag:bool):
        if ra_flag:
            self.header_flags = self.header_flags | (0x1 << 7)
        else:
            self.header_flags = self.header_flags & (0xFF7F)


    def set_rcode(self, rcode_type:RCODE_TYPE):
        self.header_flags = self.header_flags & 0xFFF8
        rcode_value = rcode_type.value
        if rcode_type==RCODE_TYPE.NO_ERROR:
            self.header_flags = self.header_flags | rcode_value
        elif rcode_type==RCODE_TYPE.FORMAT_ERROR:
            self.header_flags = self.header_flags | rcode_value
        elif rcode_type==RCODE_TYPE.SERVER_FAILURE:
            self.header_flags = self.header_flags | rcode_value
        elif rcode_type==RCODE_TYPE.NAME_ERROR:
            self.header_flags = self.header_flags | rcode_value
        elif rcode_type==RCODE_TYPE.NOT_IMPLEMENTED:
            self.header_flags = self.header_flags | rcode_value


    def set_z(self): ...


    def set_qdcount(self, query_count:int):
        self.qdcount = query_count & 0xFFFF
        pass


    def set_ancount(self, answer_count:int):
        self.ancount = answer_count & 0xFFFF


    def set_nscount(self, nameserver_count):
        self.nscount = nameserver_count & 0xFFFF


    def set_arcount(self, additional_records_count:int):
        self.arcount = additional_records_count & 0xFFFF



    
    def encode(self) -> bytearray:
        header_bytes_list = bytearray()
        
        header_message_list = [
            self.id,
            self.header_flags,
            self.qdcount,
            self.ancount,
            self.nscount,
            self.arcount
        ]
        
        for header_message in header_message_list:
            header_bytes_list = header_bytes_list + header_message.to_bytes(length=2,byteorder='big')
        
        return header_bytes_list


    def __str__(self):
        print(f"ID      : {self.id:016b}")
        print(f"FLAGS   : {self.header_flags:016b}")
        print(f"QDCOUNT : {self.qdcount:016b}")
        print(f"ANCOUNT : {self.ancount:016b}")
        print(f"NSCOUNT : {self.nscount:016b}")
        print(f"ARCOUNT : {self.arcount:016b}")
        return str(bin(int.from_bytes(self.encode(),byteorder='big')))
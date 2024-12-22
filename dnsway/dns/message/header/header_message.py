from dnsway.dns.converter.interface import DnsWaySerializer
from dnsway.dns.message.header.types import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
import random


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
        self.id_rand = 0x00
        self.header_flags = 0x00 #int(b'0x00',16)
        self.qdcount = 0x00 #int(b'0x00',16)
        self.ancount = 0x00 #int(b'0x00',16)
        self.nscount = 0x00 #int(b'0x00',16)
        self.arcount = 0x00 #int(b'0x00',16)


    def generate_id(self):
        self.id = random.randbytes(2)
    

    def set_id(self,id:int):
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


    def set_Z(self):
        '''this is for future use, should be all 0s'''
        pass


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
            self.id_rand,
            self.header_flags,
            self.qdcount,
            self.ancount,
            self.nscount,
            self.arcount
        ]
        
        for header_message in header_message_list:
            header_bytes_list = header_bytes_list + header_message.to_bytes(length=2,byteorder='big')
        
        return header_bytes_list


    def decode(self, dns_stream:bytes) -> object:
        pass


    def __str__(self):
        print(f"ID      : {self.id_rand:016b}")
        print(f"FLAGS   : {self.header_flags:016b}")
        print(f"QDCOUNT : {self.qdcount:016b}")
        print(f"ANCOUNT : {self.ancount:016b}")
        print(f"NSCOUNT : {self.nscount:016b}")
        print(f"ARCOUNT : {self.arcount:016b}")
        return str(bin(int.from_bytes(self.encode(),byteorder='big')))
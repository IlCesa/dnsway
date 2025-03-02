
from dataclasses import dataclass
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.dns_message import DnsMessage

class HeaderView():
     
     def __init__(self, id:int=0, qr:QUERY_TYPE=QUERY_TYPE.QUERY, opcode:OPCODE_TYPE=OPCODE_TYPE.QUERY,
                  rcode:RCODE_TYPE=RCODE_TYPE.NO_ERROR, aa:bool=False, ra:bool=False,
                  rd:bool=False, tc:bool=False, qdcount:int=0, ancount:int=0,
                  nscount:int=0, arcount:int=0):
          self.id = id
          self.qr = qr
          self.opcode_type = opcode
          self.rcode_type = rcode
          self.aa = aa
          self.ra = ra
          self.rd = rd
          self.tc = tc
          self.qdcount = qdcount
          self.ancount = ancount
          self.nscount = nscount
          self.arcount = arcount

     def __str__(self):
          str="%% HEADER\n"
          str+=f"% ID:{self.id} QR:{self.qr.name} OPCODE:{self.opcode_type.name} RCODE:{self.rcode_type.name}\n"
          str+=f"% AA:{self.aa} RA:{self.ra} RD:{self.rd} TC:{self.tc}\n"
          str+=f"% QDCOUNT:{self.qdcount} ANCOUNT:{self.ancount} NSCOUNT:{self.nscount} ARCOUNT:{self.arcount}\n\n"
          return str
        

class QuestionView():
     def __init__(self, domain_name:str, type_value:QTYPE_VALUES, class_value:QCLASS_VALUES):
          self.name = domain_name
          self.type_Value = type_value
          self.class_value = class_value

     def __str__(self):
          str="%% QUESTION\n"
          str+=f"% {self.name} {self.type_Value.name} {self.class_value.name}\n\n"
          return str


class RRecordView():
     def __init__(self, domain_name:str, type_value:QTYPE_VALUES, class_value:QCLASS_VALUES, ttl:int, data:str):
          self.name = domain_name
          self.type_value = type_value
          self.class_value = class_value
          self.ttl = ttl
          self.data = data
     
     def __str__(self):
          return f"% {self.name} {self.type_value.name} {self.class_value.name} {self.ttl} {self.data} \n"


class DnsMessageView():
     def __init__(self, header_view:HeaderView, question_view:QuestionView, answers_view:list[RRecordView], authorities_view:list[RRecordView],additionals_view:list[RRecordView]):
          self.header = header_view
          self.question = question_view
          self.answer_list = answers_view
          self.autorithy_list = authorities_view
          self.additional_list = additionals_view


     def __str__(self):
          out=f"{str(self.header)}{str(self.question)}"
          out+=f'%% ANSWER\n{"".join([str(k) for k in self.answer_list])}\n'
          out+=f'%% AUTORITHY\n{"".join([str(k) for k in self.autorithy_list])}\n'
          out+=f'%% ADDITIONAL\n{"".join([str(k) for k in self.additional_list])}\n'
          return out
     
 
@dataclass(frozen=True)
class ARecordView:
     address:str

     def __str__(self):
          return self.address
     

@dataclass(frozen=True)
class AAAARecordView:
     address:str
     
     def __str__(self):
          return self.address


@dataclass(frozen=True)
class CNameRecordView:
     alias:str

     def __str__(self):
          return self.alias


@dataclass(frozen=True)
class NSRecordView:
     nsdname:str

     def __str__(self):
          return self.nsdname
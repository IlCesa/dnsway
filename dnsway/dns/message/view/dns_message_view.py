
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
        

class QuestionView():
       def __init__(self, domain_name:str, type_value:QTYPE_VALUES, class_value:QCLASS_VALUES):
        self.name = domain_name
        self.type_Value = type_value
        self.class_value = class_value


class RRecordView():
      def __init__(self, domain_name:str, type_value:QTYPE_VALUES, class_value:QCLASS_VALUES, ttl:int, data:str):
        self.name = domain_name
        self.type_value = type_value
        self.class_value = class_value
        self.ttl = ttl
        self.data = data


class DnsMessageView():
     def __init__(self, header_view:HeaderView, question_view:QuestionView,
                 answer_list:list[RRecordView], autorithy_list:list[RRecordView],additional_list:list[RRecordView]):
          self.header:HeaderView = header_view
          self.question:QuestionView = question_view
          self.answer_list:list[RRecordView]  =  answer_list
          self.autorithy_list:list[RRecordView] = autorithy_list
          self.additional_list:list[RRecordView] = additional_list
     
     def __str__(self):
           str="--- HEADER SECTION ---\n\n"
           str+="--- QUESTION SECTION ---\n\n"
           str+=f"{self.question.name} {self.question.type_Value.name} {self.question.class_value.name}\n\n"
           str+="--- ANSWER SECTION ---\n\n"
           for answer in self.answer_list:
                str+=f"{answer.name} {answer.type_value.name} {answer.class_value.name} {answer.ttl} {answer.data} \n\n"
           str+="--- AUTORITHY SECTION ---\n\n"
           for autorithy in self.autorithy_list:
                str+=f"{autorithy.name} {autorithy.type_value.name} {autorithy.class_value.name} {autorithy.ttl} {autorithy.data} \n\n"
           str+="--- ADDITIONAL SECTION ---\n\n"
           for additional in self.additional_list:
                str+=f"{additional.name} {additional.type_value.name} {additional.class_value.name} {additional.ttl} {additional.data} \n\n"
           
           return str
    

  
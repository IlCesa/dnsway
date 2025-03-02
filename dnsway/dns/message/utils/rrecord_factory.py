from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES, AAAARecord, ARecord, CNameRecord, NSRecord
from abc import ABC, abstractmethod

from dnsway.dns.message.exception import DnsWayQTypeNotSupported

class ResourceRecordAbstractFactory(ABC):

    @abstractmethod
    def create_rrecord(qtype_value:str|QTYPE_VALUES, qclass_value:str|QCLASS_VALUES): ...


class ResourceRecordFactory(ResourceRecordAbstractFactory):

    def __init__(self):
        super().__init__()

    def create_rrecord(self, qtype:str|QTYPE_VALUES, qclass:str|QCLASS_VALUES):
        type_value = QTYPE_VALUES[qtype] if type(qtype) == str else qtype
        qclass_value = QCLASS_VALUES[qclass] if type(qclass) == str else qclass
        resource_record = None
        if type_value == QTYPE_VALUES.A:
            resource_record = ARecord()
        elif type_value == QTYPE_VALUES.AAAA:
            resource_record = AAAARecord()
        elif type_value == QTYPE_VALUES.CNAME:
            resource_record = CNameRecord()
        elif type_value == QTYPE_VALUES.NS:
            resource_record = NSRecord()
        else:
            print(type_value)
            raise DnsWayQTypeNotSupported("QTYPE NOT SUPPORTED YET.")
            #raise Exception("QTYPE NOT SUPPORTED YET.")
        
        return resource_record
    

# class ResourceRecordViewFactory(ResourceRecordAbstractFactory):

#     def __init__(self):
#         super().__init__()

#     def create_rrecord(self, qtype:str|QTYPE_VALUES, qclass:str|QCLASS_VALUES):
#         type_value = QTYPE_VALUES[qtype] if type(qtype) == str else qtype
#         qclass_value = QCLASS_VALUES[qclass] if type(qclass) == str else qclass
#         resource_record = None
#         if type_value == QTYPE_VALUES.A:
#             resource_record = ARecord()
#         elif type_value == QTYPE_VALUES.AAAA:
#             resource_record = AAAARecord()
#         elif type_value == QTYPE_VALUES.CNAME:
#             resource_record = CNameRecord()
#         elif type_value == QTYPE_VALUES.NS:
#             resource_record = NSRecord()
#         else:
#             print(type_value)
#             raise Exception("QTYPE NOT SUPPORTED YET.")
        
#         return resource_record
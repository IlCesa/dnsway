from abc import ABC, abstractmethod
from typing import Literal
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES, AAAARecord, ARecord, CNameRecord, MXRecord, NSRecord, PTRRecord, SOARecord, TXTRecord
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE, HeaderMessage
from dnsway.dns.message.question import QuestionMessage
from dnsway.dns.message.resource import ResourceRecordFormat
from dnsway.dns.message.utils.dns_message_view import AAAARecordView, ARecordView, CNameRecordView, DnsMessageView, HeaderView, MXRecordView, NSRecordView, PTRRecordView, QuestionView, RRecordView, SOARecordView, TXTRecordView
from dnsway.dns.message.utils.rrecord_factory import ResourceRecordFactory


class DnsWayConverter(ABC):

    @abstractmethod
    def to_view(self, dns_message_view:DnsMessageView): ...
    
    @abstractmethod
    def to_msg(self, msg_view, dnsway_message_builder:DnsMessageBuilderNew): ...


class DnsMessageConverter(DnsWayConverter):

    def to_view(self, dnsmessage:DnsMessage):
        header_view = HeaderConverter().to_view(dnsmessage.header)
        question_view = QuestionConverter().to_view(dnsmessage.question)
        answers_view = ResourceRecordFormatConverter('answer').to_view(dnsmessage.answer.rrformat_list)
        authorities_view = ResourceRecordFormatConverter('autorithy').to_view(dnsmessage.autorithy.rrformat_list)
        additionals_view = ResourceRecordFormatConverter('additional').to_view(dnsmessage.additional.rrformat_list)
        return DnsMessageView(header_view=header_view,
                              question_view=question_view,
                              answers_view=answers_view,
                              authorities_view=authorities_view,
                              additionals_view=additionals_view)
    

    def to_msg(self, dns_message_view:DnsMessageView):
        # nel mio caso d'uso credo che DnsMessageView -> DnsMessageBuilder -> DnsMessage -> DnsMessageView -> ... sia la sequenza corretta di "trasformazioni"
        # questo perche' sia il client che il resolver si troveranno a lavorare col MessageView per comodita' e poi da li il messaggio sara' trasformato nella sua rapresentazione in bytes.
        # quindi qui creo il builder e nei sotto converter passero sempre l'istanza builder e ognuno aggiungera' la propria parte
        message_builder = DnsMessageBuilderNew()      
        HeaderConverter().to_msg(dns_message_view.header, message_builder)
        QuestionConverter().to_msg(dns_message_view.question, message_builder)
        ResourceRecordFormatConverter('answer').to_msg(dns_message_view.answer_list, message_builder)
        ResourceRecordFormatConverter('autorithy').to_msg(dns_message_view.autorithy_list, message_builder)
        ResourceRecordFormatConverter('additional').to_msg(dns_message_view.additional_list, message_builder)

        # [ResourceRecordFormatConverter('answer').to_msg(k, message_builder) for k in dns_message_view.answer_list]
        # [ResourceRecordFormatConverter('autorithy').to_msg(k, message_builder) for k in dns_message_view.autorithy_list]
        # [ResourceRecordFormatConverter('additional').to_msg(k, message_builder) for k in dns_message_view.additional_list]

        return message_builder.build()

 
class HeaderConverter(DnsWayConverter):
    
    def to_view(self, header:HeaderMessage):
        return HeaderView(id=header.id.value,
                          qr=QUERY_TYPE(header.query_type),
                          opcode=OPCODE_TYPE(header.opcode.value),
                          rcode=RCODE_TYPE(header.rcode.value),
                          aa=header.aa,
                          ra=header.ra,
                          rd=header.rd,
                          tc=header.tc,
                          qdcount=header.qdcount.value,
                          ancount=header.ancount.value,
                          nscount=header.nscount.value,
                          arcount=header.arcount.value)
    
    def to_msg(self, header_view:HeaderView, dnsway_message_builder:DnsMessageBuilderNew): 
        dnsway_message_builder.header(rd=header_view.rd, ra=header_view.ra,
                                      aa=header_view.aa, tc = header_view.tc,
                                      opcode=header_view.opcode_type, qr=header_view.qr,
                                      id=header_view.id, rcode=header_view.rcode_type)


class QuestionConverter(DnsWayConverter):

    def to_view(self, question:QuestionMessage):
        return QuestionView(domain_name=question.qname.domain_name,
                            type_value=QTYPE_VALUES(question.qtype.value),
                            class_value=QCLASS_VALUES(question.qclass.value))
        
    
    def to_msg(self, question_view:QuestionView, dnsway_message_builder:DnsMessageBuilderNew): 
        dnsway_message_builder.question(qname=question_view.name,qtype=question_view.type_value,qclass=question_view.class_value)


class ResourceRecordFormatConverter(DnsWayConverter):

    def __init__(self, rrformat_type: Literal["answer", "autorithy", "additional"]):
        self.rrformat_type = rrformat_type

    
    def to_view(self, rrformat_list:ResourceRecordFormat):
        rrecord_view_list = []
        for rrformat in rrformat_list:
           #qui dobbiamo convertire il resourcerecord da "raw_msg" a "rrecord_view"
           rrecord_view = RRecordView(domain_name=rrformat.name.domain_name,
                                      type_value=QTYPE_VALUES(rrformat.type_value.value),
                                      class_value=QCLASS_VALUES(rrformat.class_value.value),
                                      ttl=rrformat.ttl.value,
                                      data=ResourceRecordConverter().to_view(rrformat.rdata.resource_record))
           rrecord_view_list.append(rrecord_view)
        return rrecord_view_list
    
    
    def to_msg(self, rrformats_view:list[RRecordView], dnsway_message_builder:DnsMessageBuilderNew): 
        qrr_factory:ResourceRecordFactory = ResourceRecordFactory()

        #qui devo convertire RRecordView.data -> nel raw resource record
        #NB: volendo fare un parallelismo tra DTO e MODEL, il dto nel nostro caso è il RAW_MSG mentre il model è il view message.
        # INTUITIVAMENTE ci viene da dire che dovrebbe essere il contrario, ma dopo giorni di "jettamento di sangue" questa dovrebbe essere la via corretta/migliore anche per gestione della persistenza e della cache (sia per il resolver che per il ns server)
        #rdata = qrr_factory.create_rrecord(resource_record_view.type_value, resource_record_view.class_value)
        
        for resource_record_view in rrformats_view:
            rdata = ResourceRecordConverter().to_msg(resource_record_view.data)
            if self.rrformat_type == 'answer':
                dnsway_message_builder.answer(name=resource_record_view.name,type_value=resource_record_view.type_value, class_value=resource_record_view.class_value, ttl=resource_record_view.ttl, rdata=rdata)
            elif self.rrformat_type == 'autorithy':
                dnsway_message_builder.autorithy(name=resource_record_view.name,type_value=resource_record_view.type_value, class_value=resource_record_view.class_value, ttl=resource_record_view.ttl, rdata=rdata)
            elif self.rrformat_type == 'additional':
                dnsway_message_builder.additional(name=resource_record_view.name,type_value=resource_record_view.type_value, class_value=resource_record_view.class_value, ttl=resource_record_view.ttl, rdata=rdata)

        # questa è la parte piu' delicata.
        #cosi' come nel decode del resource record c'è una specie di factory che serve a capire il tipo record utilizzato ed istanziare il tipo corretto.
        # qui dovra' essere fatta la stessa cosa. Il builder ha bisogno di un rdata che sara' "CnameRecord, ARecord etc"


class ResourceRecordConverter(DnsWayConverter):

    def __init__(self):
        super().__init__()


    def to_msg(self, rrecord_view):
        if isinstance(rrecord_view,ARecordView):
            return ARecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,AAAARecordView):
            return AAAARecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,CNameRecordView):
            return CNameRecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,NSRecordView):
            return NsRecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,SOARecordView):
            return SOARecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,MXRecordView):
            return MXRecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,PTRRecordView):
            return PTRRecordConverter().to_msg(rrecord_view)
        elif isinstance(rrecord_view,TXTRecordView):
            return TXTRecordConverter().to_msg(rrecord_view) 
        else:
            print("CONVERSION NOT SUPPORTED FOR TYPE",type(rrecord_view))
            pass # NOT SUPPORTED TYPE CONVERSION


    def to_view(self, rrecord):
        if isinstance(rrecord,ARecord):
            return ARecordConverter().to_view(rrecord)
        elif isinstance(rrecord,AAAARecord):
            return AAAARecordConverter().to_view(rrecord)
        elif isinstance(rrecord,CNameRecord):
            return CNameRecordConverter().to_view(rrecord)
        elif isinstance(rrecord,NSRecord):
            return NsRecordConverter().to_view(rrecord)
        elif isinstance(rrecord, SOARecord):
            return SOARecordConverter().to_view(rrecord)
        elif isinstance(rrecord,MXRecord):
            return MXRecordConverter().to_view(rrecord)
        elif isinstance(rrecord,PTRRecord):
            return PTRRecordConverter().to_view(rrecord)
        elif isinstance(rrecord,TXTRecord):
            return TXTRecordConverter().to_view(rrecord)
        else:
            print("CONVERSION NOT SUPPORTED FOR TYPE",type(rrecord))
            pass # NOT SUPPORTED TYPE CONVERSION
        pass


class ARecordConverter():
    def to_view(self, arecord:ARecord):
        rr = ARecordView(str(arecord))
        return rr

    def to_msg(self, arecord_view:ARecordView):
        arecord = ARecord()
        arecord.ip_address = arecord_view.address
        return arecord


class AAAARecordConverter():
    def to_view(self, arecord:AAAARecord):
        return AAAARecordView(str(arecord))


    def to_msg(self, aaaarecord_view:ARecordView):
        arecord = AAAARecord()
        arecord.ip_address = aaaarecord_view.address
        return arecord


class NsRecordConverter():
    def to_view(self, nsrecord:NSRecord):
        return NSRecordView(str(nsrecord))


    def to_msg(self, nsrecord_view:NSRecordView):
        nsrecord = NSRecord()
        nsrecord.alias_name = nsrecord_view.nsdname
        return nsrecord


class CNameRecordConverter():
    def to_view(self, cnamerecord:CNameRecord):
        return CNameRecordView(str(cnamerecord))


    def to_msg(self, cnamerecord_view:CNameRecordView):
        cnamerecord = CNameRecord()
        cnamerecord.alias_name = cnamerecord_view.alias
        return cnamerecord


class SOARecordConverter():
    def to_view(self, soa_record:SOARecord):
        return SOARecordView(soa_record.mname.domain_name, soa_record.rname.domain_name, soa_record.serial.value, soa_record.refresh.value, soa_record.retry.value, soa_record.expire.value, soa_record.minimum.value)


    def to_msg(self, soarecord_view:SOARecordView):
        soarecord = SOARecord()
        soarecord.rname = soarecord_view.rname
        soarecord.mname = soarecord_view.mname
        soarecord.serial = soarecord_view.serial
        soarecord.refresh = soarecord_view.refresh
        soarecord.retry = soarecord_view.retry
        soarecord.expire = soarecord_view.exprire
        soarecord.minimum = soarecord_view.minimum
        return soarecord
    




class PTRRecordConverter():
    def to_view(self, ptrrecord:PTRRecord):
        return PTRRecordView(ptrrecord.ptrdname.domain_name)
    
    def to_msg(self, ptrrecord_view:PTRRecordView):
        ptrrecord = PTRRecord()
        ptrrecord.ptrdname = ptrrecord_view.ptrdname
        return ptrrecord


class TXTRecordConverter():
    def to_view(self, txtrecord:TXTRecord):
        return TXTRecordView(txtrecord.txt_data)
    def to_msg(self, txtrecord_view:TXTRecordView):
        txtrecord = TXTRecord()
        txtrecord.txt_data = txtrecord_view.txt_data
        return txtrecord

class MXRecordConverter():
    def to_view(self, mxrecord:MXRecord):
        return MXRecordView(mxrecord.preference.value, mxrecord.exchange.domain_name)
    def to_msg(self, mxrecord_view:MXRecordView):
        print("Converting MX view to msg",mxrecord_view)
        mxrecord = MXRecord()
        mxrecord.preference = mxrecord_view.preference
        print("prima che si rompa")
        mxrecord.exchange = mxrecord_view.exchange
        print(mxrecord.encode())
        print("dopo")
        return mxrecord
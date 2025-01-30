
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_message import DnsMessage
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.dns.message.view.dns_message_view import DnsMessageView, HeaderView, QuestionView, RRecordView


class DnsMessageConverter():
    def raw_msg_to_view(self, dns_message:DnsMessage):
        header_dns = dns_message.header

        header_view = HeaderView(id=header_dns.id, qr=QUERY_TYPE(header_dns.query_type),opcode=OPCODE_TYPE(header_dns.opcode.value), rcode=RCODE_TYPE(header_dns.rcode.value), aa=header_dns.aa, ra=header_dns.ra, rd=header_dns.rd,tc=header_dns.tc, qdcount=header_dns.qdcount,ancount=header_dns.ancount, nscount=header_dns.nscount, arcount=header_dns.arcount)
        question_view = QuestionView(domain_name=dns_message.question.qname.domain_name, type_value=QTYPE_VALUES(dns_message.question.qtype.value), class_value=QCLASS_VALUES(dns_message.question.qclass.value))
        autorithy_list = dns_message.autorithy
        additional_list = dns_message.additional

        answer_list_view = []
        for rrformat in dns_message.answer.rrformat_list:
           rrecord_view = RRecordView(rrformat.name.domain_name, QTYPE_VALUES(rrformat.type_value.value), QCLASS_VALUES(rrformat.class_value.value), rrformat.ttl, rrformat.rdata.resource_record.__str__())
           answer_list_view.append(rrecord_view)

        autorithy_list_view = []
        for rrformat in autorithy_list.rrformat_list:
           rrecord_view = RRecordView(rrformat.name.domain_name, QTYPE_VALUES(rrformat.type_value.value), QCLASS_VALUES(rrformat.class_value.value), rrformat.ttl, rrformat.rdata.resource_record.__str__())
           autorithy_list_view.append(rrecord_view)

        additional_list_view = []
        for rrformat in additional_list.rrformat_list:
           rrecord_view = RRecordView(rrformat.name.domain_name, QTYPE_VALUES(rrformat.type_value.value), QCLASS_VALUES(rrformat.class_value.value), rrformat.ttl, rrformat.rdata.resource_record.__str__())
           additional_list.append(rrecord_view)
        
        dns_message_view = DnsMessageView(header_view, question_view, answer_list_view, autorithy_list_view, additional_list_view)
        return dns_message_view

    def view_to_raw_msg(self):
        raise Exception("Not implemented.")
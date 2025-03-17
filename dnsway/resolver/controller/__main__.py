import time
from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.resolver.controller.resolver import DnsWayResolverServer
import asyncio

from dnsway.resolver.service.resolver_service import DnsServerResolverServiceImpl
from dnsway.resolver.service.unit_of_work import QueryHistoryUnitOfWork

if __name__ == "__main__":    
    DnsWayResolverServer().start()


    # @DEBUG FOR TESTING PURPOSE
    # qrh_uow = QueryHistoryUnitOfWork()
    # req_msg = (DnsMessageBuilderNew().
    #              header(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY)
    #              .question(qname="www.theredcode.it", qtype='A', qclass='IN').build())
                
    # resolver_service = DnsServerResolverServiceImpl(query_history_of_work=qrh_uow)
    # start = time.time()
    # asyncio.run(resolver_service.process(DnsMessageConverter().to_view(req_msg)))
    # end = time.time()
    # print(f"{(end-start) * 1000}ms")
    # input("Press key to run next query")
    # start = time.time()
    # asyncio.run(resolver_service.process(DnsMessageConverter().to_view(req_msg)))
    # end = time.time()
    # print(f"{(end-start) * 1000}ms")

    # with qrh_uow as qru:
    #     qrh = qru.history.get("www.theredcode.it",QTYPE_VALUES.A,QCLASS_VALUES.IN)
    #     for s in qrh.slist:
    #         print(s.address,s.nsdname, s.get_score())
    #     print(qrh.sbelt)
    #     print(qrh.cache)


    
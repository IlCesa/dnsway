
from dnsway.resolver.controller.resolver import DnsWayResolverServer

def main():
    DnsWayResolverServer().start()

if __name__ == "__main__": 
    # TODO: configurazioni: porto, logger, --nocache, boh basta per ora   
    main()


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


    
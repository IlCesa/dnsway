from dnsway.dns.message.definition.resource_record import QCLASS_VALUES, QTYPE_VALUES
from dnsway.resolver.domain.resolver_model import NameServer, QueryResolutionHistory
from dnsway.dns.message.utils.dns_message_view import DnsMessageView, RRecordView
from dnsway.resolver.domain.exeptions import DnsWayResolverNameErrorException
from dnsway.resolver.service.network_service import NetworkResolverService
from dnsway.dns.message.header import OPCODE_TYPE, QUERY_TYPE, RCODE_TYPE
from dnsway.resolver.service.unit_of_work import QueryHistoryUnitOfWork
from dnsway.dns.message.utils.converter import DnsMessageConverter
from dnsway.dns.message.dns_builder import DnsMessageBuilderNew
from dnsway.dns.message.dns_message import DnsMessage
import asyncio
import abc


class AbstractResolverServiceLayer:
    @abc.abstractmethod
    def process(self) -> DnsMessageView:
        raise NotImplementedError
    

class DnsServerResolverServiceImpl(AbstractResolverServiceLayer):
    def __init__(self, query_history_of_work:QueryHistoryUnitOfWork):
        self.query_history_uow = query_history_of_work
        self.network_resolver_service = NetworkResolverService()
        self.processed_domains_list = []

        self.query_key = None #will be initialized once process method is called

    async def __update_ns_stats_callback(self, address:str, elapsed_time:float, timed_out:bool) -> None:
        # print("CALLED BACK FROM COROUTINE", address[0], elapsed_time, timed_out)
        address, port = address
        async with self.query_history_uow as qru:
            qrh:QueryResolutionHistory = qru.history.get(*self.query_key)
            ns: NameServer = qrh.get_ns_by_address(address)
            # print("FROM CALLBACK FOUND NS:",ns)
            if ns != -1:
                ns.increment_req()
                if not timed_out:
                    ns.increment_res()
                    ns.add_t(elapsed_time)
                    print("NS STATS FOR",address,"UPDATED SUCCESFULLY")

    async def process(self, dns_message_view:DnsMessageView) -> DnsMessageView:
        try:
            question = dns_message_view.question
            stuple = (question.name, question.type_value, question.class_value)
            self.query_key = stuple
            dns_message_view.header.ra = True
            dns_message_view.header.qr = QUERY_TYPE.RESPONSE
            rr_lookup_res = await self.__global_lookup(*stuple)
            sname, answers, autorithies = rr_lookup_res
            #
            # for answer in answers:
            #     print(answer.name, answer.type_value, answer.class_value, answer.ttl, answer.data)
            dns_message_view.answer_list = answers
            dns_message_view.autorithy_list = autorithies
            return dns_message_view
        except DnsWayResolverNameErrorException as drnee:
            dns_message_view.header.rcode_type = RCODE_TYPE.NAME_ERROR
            dns_message_view.autorithy_list = drnee.autorithies
            return dns_message_view
        except Exception as e:
            print(f"[{dns_message_view.header.id}] - Exception during resolution process:", e)
            return DnsServerResolverServiceImpl.DnsMessageServerFailure(dns_message_view.header.id, *stuple)


    async def __global_lookup(self, sname:str, stype:QTYPE_VALUES, sclass:QCLASS_VALUES) -> list[RRecordView]:
        initial_sname = sname
        rr_found = False
        rr_list = []
        aut_list = []
        while not rr_found:
            res = -1
            cache_response = False
            async with self.query_history_uow as qru:
                qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                res = qrh.local_lookup()

            if res != -1:
                cache_response = True
                answers = res
            else:  
                async with self.query_history_uow as qru:
                    qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                    na:NameServer = qrh.next_address(desired_addresses=4)
                    addresses = [ns.address for ns in na]
                    # print(f"Next address:{addresses}")
                msg = (DnsMessageBuilderNew().header(qr=QUERY_TYPE.QUERY,opcode=OPCODE_TYPE.QUERY).question(qname=sname, qtype=stype, qclass=sclass).build())
                recv_iteration_message_view = await self.network_resolver_service.resolve(addresses, msg, self.__update_ns_stats_callback)
            
                answers = recv_iteration_message_view.answer_list
                autorithies = recv_iteration_message_view.autorithy_list
                additionals = recv_iteration_message_view.additional_list

                if recv_iteration_message_view.header.rcode_type == RCODE_TYPE.NAME_ERROR:
                    print("here")
                    raise DnsWayResolverNameErrorException(autorithies)
                # print(recv_iteration_message_view)
                
            if answers:
                for answer in answers:
                    if stype == answer.type_value:
                        rr_list.append(answer)
                        rr_found = True
                        if not cache_response:
                            async with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache_rrecord(answer)

                    elif answer.type_value == QTYPE_VALUES.CNAME:
                        # TODO: CHECK IN THE ADDITIONAL SECTION IF THERE IS A GLUE RECORD FOR THIS CNAME
                        # EX. -> in answer troviamo C.ISI.EDU. -> in AUTORITHY troviamo l'NS SERVER ISI.EDU. E IN ADDITIONAL TROVIAMO IL RECORD A PER ISI.EDU.
                        if not cache_response:
                            async with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache_rrecord(answer)

                        sname = answer.data.alias
                        rr_list.append(answer)

            elif additionals:
                slist = []
                for additional in additionals:
                    slist.append(NameServer(additional.name, additional.data.address, additional.ttl))
                
                async with self.query_history_uow as qru:
                    qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                    qrh.set_slist(slist)

            elif autorithies:
                task_list = []
                for autorithy in autorithies:
                    autorithy:RRecordView = autorithy
                    if autorithy.type_value == QTYPE_VALUES.NS:
                        task_list.append(self.__global_lookup(autorithy.data.nsdname, QTYPE_VALUES.A, QCLASS_VALUES.IN))
                    elif autorithy.type_value == QTYPE_VALUES.SOA:
                        aut_list.append(autorithy)
                        rr_found = True
                        '''if not cache_response:
                            async with self.query_history_uow as qru:
                                qrh:QueryResolutionHistory = qru.history.get(sname, stype, sclass)
                                qrh.cache_rrecord(autorithy)'''
                
                if task_list:
                    done, pending = await asyncio.wait(task_list, return_when=asyncio.ALL_COMPLETED)
                    # dovrei iterare su tutta la lista qui per poter aggiungere tutte le nuove delegazioni eventualmente responsabili per la risoluzione della seguente query
                    # probema -> aspettare tutti riduce il tempo totale di risoluzione (la prima volta) ma ci da' piu' opzioni per le risoluzioni successive (una volta cachate)
                    slist = []
                    while len(done) > 0:
                        nsdname, ns_list,au_list = done.pop().result()
                        print(nsdname, ns_list)
                        slist.extend([NameServer(nsdname, nsrecord.data.address) for nsrecord in ns_list])
                    async with self.query_history_uow as qru:
                            qrh:QueryResolutionHistory = qru.history.get(sname,stype,sclass)
                            qrh.set_slist(slist)
            else:
                raise Exception('NO RESPONSE FOUND')

        return (initial_sname, rr_list, aut_list)


    @staticmethod
    def DnsMessageNotImplemented(id:int, domain_name:str) -> DnsMessage:
        msg = (DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.NOT_IMPLEMENTED,opcode=OPCODE_TYPE.QUERY)
                # .question(qname=domain_name, qtype=QTYPE_VALUES.A, qclass=QCLASS_VALUES.IN)
                .build())
        return DnsMessageConverter().to_view(msg)


    @staticmethod
    def DnsMessageNameError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.NAME_ERROR).build()
        return DnsMessageConverter().to_view(msg)
    

    @staticmethod
    def DnsMessageFormatError(id:int) -> DnsMessage:
        msg = DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.FORMAT_ERROR).build()
        return DnsMessageConverter().to_view(msg)


    @staticmethod
    def DnsMessageServerFailure(id:int, domain_name:str, qtype, qclass) -> DnsMessage:
        msg = (DnsMessageBuilderNew().header(rd=True, ra=True, id=id, rcode=RCODE_TYPE.SERVER_FAILURE, qr=QUERY_TYPE.RESPONSE, opcode=OPCODE_TYPE.QUERY)
               .question(qname=domain_name, qtype=qtype, qclass=qclass)
               .build())
        return DnsMessageConverter().to_view(msg)
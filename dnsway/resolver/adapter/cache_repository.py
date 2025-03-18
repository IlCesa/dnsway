from dnsway.resolver.domain.resolver_model import QueryResolutionHistory
from dnsway.resolver.adapter.sbelt_repository import SBeltRepository
import abc


class AbstractQueryRepository():
    @abc.abstractmethod
    def add(self, rrecord):
        raise NotImplementedError
    @abc.abstractmethod
    def get(self, domain_name):
        raise NotImplementedError
    @abc.abstractmethod
    def delete(self, domain_name):
        raise NotImplementedError


class InMemoryQueryRepository(AbstractQueryRepository):
    def __init__(self):
        self.query_history_dict:dict[QueryResolutionHistory] = {}
        self.sbelt_repo = SBeltRepository('dnsway/resolver/data/root.txt')
        # self.__wlocks = {}
        # self.__rlocks = {}

    def add(self, qrh: QueryResolutionHistory):
        qrh_key = (qrh.sname, qrh.stype, qrh.sclass)
        self.query_history_dict[qrh_key] = qrh

    def get(self, sname, stype, sclass):
        qrh_key = (sname,stype,sclass)
        if  qrh_key not in self.query_history_dict:
            self.query_history_dict[qrh_key] = QueryResolutionHistory(sname,stype,sclass,sbelt=self.sbelt_repo.list())
        
        return self.query_history_dict[qrh_key]


    def delete(self, domain_name):
        raise NotImplementedError
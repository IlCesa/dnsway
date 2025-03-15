import abc
from dnsway.resolver.adapter.sbelt_repository import SBeltRepository
from dnsway.resolver.domain.resolver_model import QueryResolutionHistory
from dnsway.server.domain.resolver_model import RequestResourceState


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
    
    

'''
class InMemoryRepository():
    def __init__(self):
        self.request_resource_state_dict = {}


    def add(self, domain_name, rrs:RequestResourceState):
        if domain_name not in self.request_resource_state_dict:
            self.request_resource_state_dict[domain_name] = []

        self.request_resource_state_dict[domain_name].append(rrs)
    

    def get(self, sname, stype, sclass):
        rr_list = self.request_resource_state_dict[sname]
        # qui filtro solo gli stype ed sclass desiderati
        return rr_list[0] # per ora come test ritorno il primo elemento della lista
    

    def delete(self, sname, stype, sclass):
        print("Rimuovo")
'''

# class RedisCacheRepository(AbstractCacheRepository):

#     def __init__(self):
#         pass

#     def add(self, rrecord:RRecord):
#         raise NotImplementedError
    
#     def get(self, domain_name):
#         raise NotImplementedError
    
#     def delete(self, domain_name):
#         raise NotImplementedError


# class InMemoryRepository(AbstractCacheRepository):
#     def __init__(self):
#         self.rrecord_cache_dict = {}


#     def add(self, rrecord:RRecord):
#         if rrecord.domain_name not in self.rrecord_cache_dict:
#             self.rrecord_cache_dict[rrecord.domain_name] = []
#         self.rrecord_cache_dict[rrecord.domain_name].append(rrecord)
    

#     def get(self, domain_name, qtype):
#         for rrecord in self.rrecord_cache_dict[domain_name]:
#             # check timestamp validity here
#             if rrecord.type_value == qtype:
#                 return rrecord
#         return -1
    
    
#     def delete(self, domain_name):
#         raise NotImplementedError
    

# class SqlAlchemyRepository(AbstractRepository):
#     def __init__(self, session):
#         self.session = session
#     def add(self, batch):
#         self.session.add(batch)
#     def get(self, reference):
#         pass
#         #return self.session.query(model.Batch).filter_by(reference=reference).one()
#     def list(self):
#         pass
#         #return self.session.query(model.Batch).all()
    

# class FileRepository(AbstractRepository):
#     pass

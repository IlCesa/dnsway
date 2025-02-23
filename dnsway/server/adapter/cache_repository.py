import abc
from dnsway.server.domain.resolver_model import RRecord


class AbstractCacheRepository():
    @abc.abstractmethod
    def add(self, rrecord:RRecord):
        raise NotImplementedError
    @abc.abstractmethod
    def get(self, domain_name):
        raise NotImplementedError
    @abc.abstractmethod
    def delete(self, domain_name):
        raise NotImplementedError


class RedisCacheRepository(AbstractCacheRepository):
    pass


class InMemoryRepository(AbstractCacheRepository):
    def __init__(self):
        self.rrecord_cache_dict = {}


    def add(self, rrecord:RRecord):
        if rrecord.domain_name not in self.rrecord_cache_dict:
            self.rrecord_cache_dict[rrecord.domain_name] = []
        self.rrecord_cache_dict[rrecord.domain_name].append(rrecord)
    

    def get(self, domain_name, qtype):
        for rrecord in self.rrecord_cache_dict[domain_name]:
            # check timestamp validity here
            if rrecord.type_value == qtype:
                return rrecord
        return -1
    
    
    def delete(self, domain_name):
        raise NotImplementedError
    

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

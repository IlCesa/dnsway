import abc


class AbstractCacheRepository():
    @abc.abstractmethod
    def add(self):
        raise NotImplementedError
    @abc.abstractmethod
    def get(self):
        raise NotImplementedError
    

class RedisCacheRepository():
    pass
    

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

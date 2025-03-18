# il servizio unit of work è usato dal service layer per accedere al repository
# nu macell comunq

from contextlib import asynccontextmanager
from dnsway.resolver.adapter.cache_repository import InMemoryQueryRepository
from typing import Optional
import asyncio


class AbstractUnitOfWork():
    def __init__(self):
        pass


class QueryHistoryUnitOfWork():
    def __init__(self):
        self.history = InMemoryQueryRepository()
        self.history_locks = {}
        self._committed = False

        self.lock = asyncio.Lock()
    
    async def __aenter__(self):
        await self.lock.acquire()
        self._committed = False
        return self


    '''@asynccontextmanager
    async def get(self, sname, stype, sclass):
        await self.lock.acquire()
        skey = (sname,stype,sclass)
        if skey not in self.history_locks:
            self.histoty_locks[skey] = asyncio.Lock()
        slock = self.histoty_locks[skey]
        self.lock.release()

        await slock.acquire()
        yield self.history.get(sname, stype, sclass)
        slock.release()'''
    
    
    def commit(self):
        self._committed = True
    
    def rollback(self):
        pass
        #self.repository.data.clear()
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        self.lock.release()
        if exc_type:
            self.rollback()
        else:
            self.commit()



# class RedisUnitOfWork:
#     def __init__(self, redis_url: str = "redis://localhost"):
#         self.redis_url = redis_url  # URL per connettersi a Redis
#         self.redis: Optional[aioredis.Redis] = None  # Connessione Redis
#         self.repository: Optional[RedisRepository] = None  # Repository Redis
#         self.pipeline = None  # Pipeline Redis

#     async def __aenter__(self):
#         self.redis = await aioredis.from_url(self.redis_url)  # Connessione a Redis
#         self.repository = RedisRepository(self.redis)  # Inizializzo il repository
#         self.pipeline = self.redis.pipeline()  # Attivo pipeline per batch di operazioni
#         return self

#     async def __aexit__(self, exc_type, exc, tb):
#         if exc is None:
#             await self.commit()  # Se tutto OK, confermo
#         else:
#             await self.rollback()  # Se errore, annullo (soft rollback)
#         await self.redis.close()  # Chiudo connessione Redis

#     async def commit(self):
#         """Esegue i comandi nella pipeline."""
#         await self.pipeline.execute()

#     async def rollback(self):
#         """Non è possibile annullare operazioni in Redis, quindi resetto la pipeline."""
#         self.pipeline = self.redis.pipeline()
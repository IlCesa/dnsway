# il servizio unit of work è usato dal service layer per accedere al repository
# nu macell comunq

import asyncio
from contextlib import asynccontextmanager
import threading
from typing import Optional

from dnsway.resolver.adapter.cache_repository import InMemoryQueryRepository
from dnsway.server.adapter.cache_repository import AbstractCacheRepository, InMemoryRepository

class AbstractUnitOfWork():
    def __init__(self):
        self.repository: AbstractCacheRepository = None


class QueryHistoryUnitOfWork():
    def __init__(self):
        self.history = InMemoryQueryRepository()
        self._committed = False

        self.lock = asyncio.Lock()
    
    async def __aenter__(self):
        await self.lock.acquire()
        self._committed = False
        return self
    
    
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
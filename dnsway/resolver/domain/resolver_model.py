from dnsway.dns.message.utils.dns_message_view import RRecordView
from dataclasses import dataclass
import math
import time


@dataclass(frozen=True)
class RRecordCacheView:
   rrecord_view:RRecordView
   absolute_ttl_time:int

class NameServer:
   def __init__(self, ns:str, address:str, ttl:int = None):
      self.nsdname = ns
      self.address = address
      self.ttl = ttl
      self.__w = [0.5, 0.25, 0.15, 0.07, 0.03]
      self.__t = [1] * 5 # questa è una bella question, quanto dovrebbe essere il tempo medio iniziale? l'rfc indica come valore "scarso" 5s oppure 10s, quindi usero' un approccio "ottimistico" dove "A FIDUCIA" indico i tempi medi di ogni ns come "buoni" e poi se nelle varie richieste supereranno i 5s li scarto via.
      self.__req = 0
      self.__res = 0

      self.__t_index = 0
   
   def increment_req(self):
      self.__req = self.__req + 1

   def increment_res(self):
      self.__res = self.__res + 1

   def add_t(self, t:int):
      self.__t[self.__t_index] = t
      self.__t_index = (self.__t_index + 1) % 5

   def weighted_response(self):
      return sum(x*y for x,y in zip(self.__w, self.__t))

   def batting_average(self): # 0 -> worst case, 1 -> ideal case
      if self.__req == 0:
         return 0
      return self.__res / self.__req
   
   def get_score(self):
      # NB: il prodotto scalare nel mio caso non va bene perche' avendo come riferimento (1,0) weighted_response nella misurazione. La cosine similarity sarebbe l'ideale visto che i moduli dei vettori influisocno sul risultato. Per ora usero' una banale distanza euclidea.
      return math.sqrt((1 - self.batting_average())**2 + (0 - self.weighted_response())**2)

   def __str__(self):
      return f"{self.nsdname} {self.address} {self.batting_average()} {self.weighted_response()} {self.get_score()}"

#TODO: Should depends on abstraction that define the desired "behavior" ex. cache_record, next_addres etc.
class QueryResolutionHistory:
   def __init__(self, sname, stype, sclass, sbelt):
      self.sname = sname
      self.stype = stype
      self.sclass = sclass
      self.sbelt = sbelt # reference to root belt list
      self.slist = [] # a list of last known delegation nameservers for sname,stype,sclass query
      self.cache = []
      self.match_count = -1 # an euristic about the 'distance' between slist delegations and sname, must be initialized with -1
      self.__reset_slist()

   def get_ns_by_address(self, address):
      all_ns_list = set(self.slist + self.sbelt)
      for ns in all_ns_list:
         if ns.address == address:
            return ns
      return -1

   def next_address(self, desired_addresses:int=1, score_cutoff:int = 5):
      # and ':' not in x.address
      #TODO: aggiungere check ttl anche per i ns server HERE
      self.slist = list(filter(lambda x:x.get_score() < score_cutoff, self.slist))
      if self.slist:
         s = sorted(self.slist,  key=lambda x: x.get_score())
         return s[:desired_addresses]
      else:
         self.slist = self.sbelt # all delegations are expired or the score is too low to keep the record
         return self.slist[:desired_addresses]

   def set_slist(self, delegations_list:list[NameServer]):
      self.slist = delegations_list
      self.__update_mc()

   def cache_rrecord(self, rrecord:RRecordView):
      absolute_ttl_time = int(time.time()) + int(rrecord.ttl)
      self.cache.append(RRecordCacheView(rrecord,absolute_ttl_time))

   def local_lookup(self) -> RRecordView:
      self.cache = list(filter(lambda x: x.absolute_ttl_time - int(time.time()) >= 0, self.cache))
      if self.cache:
         cached_rrecord = [rrecord_cache.rrecord_view for rrecord_cache in self.cache]
         return cached_rrecord
      return -1

   def __update_mc(self):
      s1 = self.sname.split('.')
      s2 = self.slist[0].nsdname.split('.') # qui prendo il primo della lista perche' di solito i ns autorithy ricevuti sono "simili" tra loro
      # print(s1,s2)
      s1.reverse()
      s2.reverse()
      self.match_count = sum(1 for x, y in zip(s1, s2) if x == y)

   def calculate_match_count(self, nsdname1:str, nsdname2:str):
      s1 = nsdname1.split('.')
      s2 = nsdname2.split('.')
      s1.reverse()
      s2.reverse()
      return sum(1 for x, y in zip(s1, s2) if x == y)

   def __reset_slist(self):
      self.slist = self.sbelt
      self.match_count = -1
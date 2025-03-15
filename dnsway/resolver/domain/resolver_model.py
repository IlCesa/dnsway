import math
from dnsway.dns.message.utils.dns_message_view import RRecordView
import threading

class NameServer:
   def __init__(self, ns:str, address:str, ttl:int = None):
      self.nsdname = ns
      self.address = address
      self.ttl = ttl
      self.__w = [0.5, 0.25, 0.15, 0.07, 0.03]
      self.__t = [5] * 5
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
      # return (self.batting_average(), self.weighted_response())

   def __str__(self):
      return f"{self.nsdname} {self.address} {self.batting_average()} {self.weighted_response()} {self.get_score()}"


# class NameServer:
#    def __init__(self, ns:str, address:str = None):
#       self.ns = ns # zone nameserver
#       self.address:list[Address] = []

#       if address:
#          self.add_address(address)

#    def add_address(self, address:str) -> None:
#       self.address.append(Address(address))
   
#    def get_address(self, address:str) -> Address:
#       for addr in self.address:
#          if addr.address == address:
#             return addr
#       return -1


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

   def next_address(self) -> NameServer:
      s = sorted(self.slist,  key=lambda x: x.get_score())
      # qui dovrei capire se ci sono score molto bassi, se si li rimuovo dalla lista.
      # se la lista resta senza elemento reinizializzo slist con la sbelt.
      for k in s:
         print(k)
      s = list(filter(lambda k:':' not in k.address, s))
      #print(s[0].get_score(), s[0].nsdname, s[0].address)
      return s[:4]

   def set_slist(self, delegations_list:list[NameServer]):
      # nel mio caso che sto seguendo fedelmente l'rfc potrei, invece di resettare la lista, mantenere tutti i nameserver con distanza matchcount minima.
      self.slist = delegations_list
      self.__update_mc()

   def add_rrecord(self, rrecord:RRecordView):
      self.cache.append(rrecord)

   def local_lookup(self) -> RRecordView:
      if self.cache:
         return self.cache
      return -1

   def __update_mc(self):
      s1 = self.sname.split('.')
      s2 = self.slist[0].nsdname.split('.') # qui prendo il primo della lista perche' di solito i ns autorithy ricevuti sono "simili" tra loro
      # print(s1,s2)
      s1.reverse()
      s2.reverse()
      self.match_count = sum(1 for x, y in zip(s1, s2) if x == y)

   def __reset_slist(self):
      self.slist = self.sbelt
      self.match_count = -1
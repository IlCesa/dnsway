import time
from dnsway.dns.message.utils.dns_message_view import RRecordView
from dataclasses import dataclass


@dataclass(frozen=True)
class RootServer:
   domain_name : str
   ipv4 : str
   ipv6 : str


@dataclass(frozen=True)
class RRecord():
   domain_name : str
   type_value : str
   class_value : str
   absolute_ttl : int
   data : bytearray



class NameServerStat:
   def __init__(self, zone_name, address):
      self.nsdname = zone_name
      self.address = address
      self.match_count = 0

      self.aging = 0
      self.__buffer_len = 20
      self.__current_len = 20
      self.__counter = 0

      self.response_time = [1] * self.__buffer_len
   
   def get_current_len(self):
      return self.__current_len


   def add_response_time(self, rt):
      self.response_time[self.__counter % self.__buffer_len] = rt
      self.__counter = (self.__counter + 1) % self.__buffer_len
      if self.__current_len < self.__buffer_len:
         self.__current_len += 1


   def get_moving_average(self):
      num_sample = self.__current_len
      return sum([s/num_sample for s in self.response_time[:num_sample]])


class RequestResourceState:

   def __init__(self, sname, stype, sclass):
      self.sname = sname
      self.stype = stype
      self.sclass = sclass
      self.slist:list[NameServerStat] = []
      self.sbelt:list[NameServerStat] = []
      self.cache:list[RRecordView] = []

      self.__bootstrap_sbelt()


   def __bootstrap_sbelt(self):
      print("Inizializzo sbelt per",self.sname,self.stype,self.sclass)

   def add_cache(self, rrecord_view:RRecordView):
      self.cache.append(rrecord_view)

   def local_lookup(self):
      for i,rr_cache in enumerate(self.cache[:]):
         if time.time() < rr_cache.absolute_ttl:
            return rr_cache
         else:
            self.cache.pop(i)
      return None
   

   def add_nameserver(self, ns_stat:NameServerStat):
      self.slist.append(ns_stat)

   
   def remove_nameserver(self, address:str):
      print("rimuovo",address,"dalla slist")
      pass


   def get_next_nameserver(self):

      if not self.slist:
         return None
      
      sorted_slist = sorted(self.slist, key=lambda ns_stat: (ns_stat.match_count,ns_stat.get_moving_average()))
      print(sorted_slist)
      best_ns = sorted_slist[-1]
      return best_ns







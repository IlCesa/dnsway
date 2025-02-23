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
   ttl : int
   issued_timestamp : int
   data : bytes




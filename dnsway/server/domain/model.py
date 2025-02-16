from dataclasses import dataclass


@dataclass(frozen=True)
class RootServer:
   domain_name: str
   ipv4: str
   ipv6: str
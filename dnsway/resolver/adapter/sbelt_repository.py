from dnsway.resolver.domain.resolver_model import NameServer
import abc


class AbstractRootRepository():
    @abc.abstractmethod
    def list(self):
        raise NotImplementedError
    def parse(self, path):
        raise NotImplementedError


class SBeltRepository(AbstractRootRepository):
    def __init__(self, sbelt_path):
        self.sbelt = []
        self.parse(sbelt_path)

    def list(self) -> list:
        return self.sbelt

    def parse(self, sbelt_path) -> None:
        with open(sbelt_path,encoding='utf-8',mode='r') as f:
            for line in f.readlines():
                name,ipv4,ipv6  = tuple(line.strip().split(' '))
                self.sbelt.append(NameServer(ns=name,address=ipv4))
                self.sbelt.append(NameServer(ns=name,address=ipv6))
import abc
from dnsway.server.domain.model import RootServer


class AbstractRootRepository():
    @abc.abstractmethod
    def list(self):
        raise NotImplementedError
    @abc.abstractmethod
    def get(self):
        raise NotImplementedError

   
class FileRootRepository(AbstractRootRepository):
    def __init__(self, root_filepath):
        self.root_filepath = root_filepath
        self.rootserver_list = self.__parse()

    def list(self) -> list:
        return self.rootserver_list
    

    def get(self):
        return self.rootserver_list[0]


    def __parse(self):
        root_list = []
        with open(self.root_filepath,encoding='utf-8',mode='r') as f:
            for line in f.readlines():
                name,ipv4,ipv6  = tuple(line.strip().split(' '))
                root_list.append(RootServer(domain_name=name,ipv4=ipv4,ipv6=ipv6))
        return root_list

class DnsWayResolverNameErrorException(Exception):
    def __init__(self, autorithies):
        super().__init__(autorithies)
        self.autorithies = autorithies
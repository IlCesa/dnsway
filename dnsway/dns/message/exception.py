

class DnsWayEncoderNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DnsWayDumpingNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)

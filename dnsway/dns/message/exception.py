class DnsWayEncoderNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DnsWayDumpingNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DnsWayDecoderNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DnsWayMultipleQuestionNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DnsWayQTypeNotSupported(Exception):
    def __init__(self, *args):
        super().__init__(*args)

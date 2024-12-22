
# this class implementation is about "answer, Authority and additional section of the dns message format"
class ResourceRecordFormat():
    def __init__(self):
        self.name = 0x00
        self.type = 0x00 # enum here
        self.class_value = 0x00 #enum here
        self.ttl = 0x00 # unsigned 32 bit value here, represent the maximum cachable time of the resource
        self.rd_length = 0x00 # represent the length (in octets) of rdata section
        self.rdata = 0x00 # will be an object dependency

    @property
    def name(self):
        pass



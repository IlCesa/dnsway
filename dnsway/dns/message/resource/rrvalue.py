from enum import Enum


class QTYPE_VALUES(Enum):
    A               =   0x1     # a host address
    NS              =   0x2     # an authoritative name server
    MD              =   0x3     # a mail destination (Obsolete - use MX)
    MF              =   0x4     # a mail forwarder (Obsolete - use MX)
    CNAME           =   0x5     # the canonical name for an alias
    SOA             =   0x6     # marks the start of a zone of authority
    MB              =   0x7     # a mailbox domain name (EXPERIMENTAL)
    MG              =   0x8     # a mail group member (EXPERIMENTAL)
    MR              =   0x9     # a mail rename domain name (EXPERIMENTAL)
    NULL            =   0xA     # a null RR (EXPERIMENTAL)
    WKS             =   0xB     # a well known service description
    PTR             =   0xC     # a domain name pointer
    HINFO           =   0xD     # host information
    MINFO           =   0xE     # mailbox or mail list information
    MX              =   0xF     # mail exchange
    TXT             =   0x10    # text strings
    AXFR            =   0xFC    # A request for a transfer of an entire zone
    MAILB           =   0xFD    # A request for mailbox-related records (MB, MG or MR)
    MAILA           =   0xFE    # A request for mail agent RRs (Obsolete - see MX)
    ALL             =   0xFF    # A request for all records


class QCLASS_VALUES(Enum):
    IN              =   0x1     # the Internet
    CS              =   0x2     # the CSNET class (Obsolete - used only for examples in some obsolete RFCs)
    CH              =   0x3     # the CHAOS class
    HS              =   0x4     # Hesiod [Dyer 87]
    ALL             =   0xFF    # any class
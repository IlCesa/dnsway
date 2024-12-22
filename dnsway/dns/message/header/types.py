from enum import Enum


class QUERY_TYPE(Enum):
    QUERY           =   0x7FFF  # a query message
    RESPONSE        =   0x8000  # a response message


class OPCODE_TYPE(Enum):
    QUERY           =   0x0 # standard query
    IQUERY          =   0x1 << 11 # inverse querys
    STATUS          =   0x2 << 11 # server status request


class RCODE_TYPE(Enum):
    NO_ERROR        =   0x0     # No error condition
    FORMAT_ERROR    =   0x1     # Format error - The name server was unable to interpret the query.
    SERVER_FAILURE  =   0x2     # Server failure - The name server was unable to process this query due to a problem with the name server.
    NAME_ERROR      =   0x3     # Response only from an autorithative server. The requested domain name does not exists
    NOT_IMPLEMENTED =   0x4     # The name server does not support the requested kind of query.
    REFUSED         =   0x5     # The name server refuses to perform the operation for policy reason. For example the name server may not wish to provide the information.
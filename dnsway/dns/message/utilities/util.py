def domain_name_to_bytes_definition(domain_name:str) -> bytearray:
    '''convert domain string to domain name space definition of rfc1035'''
    qname = bytearray()
    '''domain name param example: www.google.it'''
    #1) contiene punti?
    #2) ogni label ha una struttura corretta?
    #per ora assumiamo di si.
    # "3 www" -> "6 google" -> "2 it" -> "000000"
    #TODO: prevedere un meccanismo di compressione del messaggio tramite gestione dei puntatori (vedere 4.1.4. Message compression)

    subdomain_list = domain_name.split('.')
    print(f"{subdomain_list}")

    for subdomain in subdomain_list:
        print(f"processing subdomain: {subdomain}")
        subdomain_length = len(subdomain)
        length_octet = subdomain_length & 0x3F #maschera per prendere solo i primi 6 bit
        qname.append(length_octet)
        print(f"adding length byte: {qname}")

        for subdomain_char in subdomain:
            letter = ord(subdomain_char) & 0xFF #maschera per estrarre 8 bit
            qname.append(letter)

    #adding zero null octet as octet qname termination.
    qname.append(0x00)
    print(f"qname after full process: {qname}")
    return qname
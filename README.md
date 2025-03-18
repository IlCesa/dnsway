# DnsWay

DnsWay is a lightweight implementation of DNS protocol, built in Python.  
It aims to provide a way to understand and work with DNS.

## 🚀 Features

- ✅ **RFC1034/1035** - Full support for DNS fundamentals
- ❌ **EDNS0** - Extended DNS support
- ❌ **DNSSEC** - Dns Security 

---

## 📦 Installation

To install DnsWay, clone the repository and install dependencies:

```bash
# Clone the repository
git clone https://github.com/IlCesa/dnsway.git
cd dnsway

# Install dependencies
pip install .
```

<!--
Or install via pip (if available):

```bash
pip install dnsway
```

-->

---

## 🔍 Client Mode

DnsWay can be used as a client to query DNS records.

```bash
python -m dnsway.client www.google.it --resolver=8.8.8.8 --port=53 --qtype=A
```

Example output:
```
%% HEADER
% ID:33944 QR:RESPONSE OPCODE:QUERY RCODE:NO_ERROR
% AA:0 RA:1 RD:1 TC:0
% QDCOUNT:1 ANCOUNT:1 NSCOUNT:0 ARCOUNT:0

%% QUESTION
% www.google.it. A IN

%% ANSWER
% www.google.it. A IN 300 142.251.209.35
```

---

## 🔄 Resolver Mode

Run DnsWay as a resolver to forward queries to upstream DNS servers.

```bash
python -m dnsway.resolver
DnsWay Udp Resolver listening on: 127.0.0.1:5353
```

This mode allows handling recursive queries by forwarding them to authoritative name servers.

---


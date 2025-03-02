# DnsWay
## 🌐 A Simple Python Implementation of RFC 1034/1035

DnsWay is a lightweight and educational implementation of DNS protocols, built in Python. It aims to provide a simple yet effective way to understand and work with DNS.

## 🚀 Features

- ✅ **RFC1034/1035** - Full support for DNS fundamentals
- ❌ **EDNS0** - Extended DNS support (Coming soon!)
- ❌ **DNSSEC** - Not yet supported (Coming soon!)

---

## 📦 Installation

To install DnsWay, clone the repository and install dependencies:

```bash
# Clone the repository
git clone https://github.com/yourusername/dnsway.git
cd dnsway

# Install dependencies
pip install -r requirements.txt
```

Or install via pip (if available):

```bash
pip install dnsway
```

---

## 🔍 Client Mode

DnsWay can be used as a client to query DNS records.

```bash
python dnsway.py --client --domain example.com
```

Example output:
```
A record for example.com: 93.184.216.34
```

---

## 🔄 Resolver Mode

Run DnsWay as a resolver to forward queries to upstream DNS servers.

```bash
python dnsway.py --resolver --port 5353
```

This mode allows handling recursive queries by forwarding them to authoritative name servers.

---

## 🏠 Local NameServer

DnsWay can act as a local authoritative name server.

```bash
python dnsway.py --nameserver --zone example.zone
```

Where `example.zone` is a file defining DNS records for your local domain.

---

🔧 **Contributions welcome!** Feel free to report issues or suggest improvements.


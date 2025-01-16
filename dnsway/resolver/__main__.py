import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="DNS Query Tool")
    parser.add_argument("--qtype", choices=["A", "AAAA", "CNAME"], help="Il tipo di record dns",default='A')
    parser.add_argument("--qclass", choices=["IN", "CH"], help="La classe DNS: IN (Internet) o CH (Chaos)", default='IN')
    parser.add_argument("--mode", choices=["R", "I"], help="R=Recursive I=Iterative",default='R')
    parser.add_argument("--resolver", type=str, help="L'indirizzo IP del resolver (richiesto solo in modalità recursive)", default='8.8.8.8')
    parser.add_argument("--domain_name", type=str, help='Domain Name to resolve')

    args,kargs = parser.parse_known_args()
    print(kargs)
    if args.mode == "I":
        print("Il resolver sara' ignorato")

    print(f"TYPE: {args.qtype}")
    print(f"CLASS: {args.qclass}")
    print(f"MODE: {args.mode}")
    if args.resolver:
        print(f"RESOLVER: {args.resolver}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python
import argparse,sys

def encrypt(domains_path, account_key, domain_key, update, csr, acme_dir):
  domaincn=""
  lines=[]
  try:
    f = open(domains_path,"r")  
    lines = f.readlines()
  finally:
    f.close()

  domains = []
  for line in lines:
    if line.strip() != "":
      domains.append(line.strip())
  
  if len(domains) == 1:
    domaincn="/CN="+domains[0]
  elif len(domains) > 0:
    domaincn="[SAN]\nsubjectAltName="
    domain=",DNS:".join(domains)
    domaincn = domaincn + "DNS:" + domain

  if os.path.isfile(account_key) == False:
    os.system("openssl genrsa 4096 > " + account_key)
  
  if os.path.isfile(domain_key) == False:
    os.system("openssl genrsa 4096" + domain_key)
  
  if update == True:
    if os.path.isfile(csr) == False:
      raise ValueError('Illegal csr path: %s' % csr)
  else:
    os.system('openssl req -new -sha256 -key ' + domain_key + ' -subj "/" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf '+domaincn+')) > '+csr)
  
  # TODO gen signed.crt and chained.pem
  if os.path.isfile('./intermediate.pem') == False:
    os.system('wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > ./intermediate.pem')

  os.remove('./chained.pem')
  os.remove('./signed.crt')

  os.system('python acme_tiny.py --account-key '+account_key+' --csr '+csr+' --acme-dir '+acme_dir+' > ./signed.crt')
  os.system('cat signed.crt intermediate.pem > chained.pem')
  
def main(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--domains", required=True, help="path to your domains")
    parser.add_argument("--account-key", required=True, default="./account.key", help="path to your Let's Encrypt account private key")
    parser.add_argument("--domain-key", required=True, default="./domain.key", help="path to your Let's domains private key")
    parser.add_argument("--acme-dir", required=True, default="./", help="path to the .well-known/acme-challenge/ directory")
    parser.add_argument("--csr", required=True, default="./domain.csr", help="path to your certificate signing request")
    parser.add_argument("--update", action='store_true', help="update cert but not recreate one. csr file needs exist.")

    args = parser.parse_args(argv)
    encrypt(args.domains, args.account_key, args.domain_key, args.update, args.csr, args.acme_dir)

if __name__ == "__main__": # pragma: no cover
    main(sys.argv[1:])

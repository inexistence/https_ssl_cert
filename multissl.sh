#!/bin/bash
find ./ -type f -name chained.pem -mtime +60 | xargs rm -rf

domaincn="[SAN]\nsubjectAltName=DNS:a.com,DNS:b.com"

if [ ! -f "acme_tiny.py" ];then
wget https://raw.githubusercontent.com/diafygi/acme-tiny/master/acme_tiny.py
fi

# generate Let's Encrypt account key
if [ ! -f "account.key" ];then
openssl genrsa 4096 > account.key
fi

# create CSR (CERTIFICATE SIGNING REQUEST)
if [ ! -f "domain.key" ];then
openssl genrsa 4096 > domain.key
fi

if [ ! -f "multidomain.csr" ];then
openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf $domaincn)) > multidomain.csr
fi

# get crt
if [ ! -f "chained.pem" ];then
find ./ -type f -name chained.pem | xargs rm -rf
find ./ -type f -name signed.crt | xargs rm -rf
find ./ -type f -name intermediate.pem | xargs rm -rf

# get wanted signed.crt, but Let's Encrypt needs combine
python acme_tiny.py --account-key account.key --csr multidomain.csr --acme-dir ./ > signed.crt

# combine Let's Encrypt intermediate.pem & signed.crt
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat signed.crt intermediate.pem > chained.pem
fi

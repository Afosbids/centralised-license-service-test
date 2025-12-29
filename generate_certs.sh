#!/bin/bash
# Generate self-signed SSL certificates for local development

mkdir -p nginx/certs
cd nginx/certs

echo "Generating self-signed SSL certificate..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key -out server.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

echo "Certificates generated in nginx/certs/"
ls -l

#!/usr/bin/env sh

mkdir -p /app/configs

if [ -f /app/configs/jwtRS256.key]; then
  if [ -f /app/configs/jwtRS256.key.pub]; then
    echo "Reusing existing JWT key"
  else
    echo "JWT private key is given but not its public key"
    exit 1
  fi
else
  ssh-keygen -t rsa -N '' -b 4096 -m PEM -f /app/configs/jwtRS256.key
  openssl rsa -in /app/configs/jwtRS256.key -pubout -outform PEM -out /app/configs/jwtRS256.key.pub
  "JWT private and public keys are created."
fi

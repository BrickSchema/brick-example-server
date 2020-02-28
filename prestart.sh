#!/usr/bin/env sh

mkdir /app/configs

ssh-keygen -t rsa -N '' -b 4096 -m PEM -f /app/configs/jwtRS256.key
openssl rsa -in /app/configs/jwtRS256.key -pubout -outform PEM -out /app/configs/jwtRS256.key.pub

#!/usr/bin/env sh

ssh-keygen -t rsa -N '' -b 4096 -m PEM -f configs/jwtRS256.key
openssl rsa -in configs/jwtRS256.key -pubout -outform PEM -out configs/jwtRS256.key.pub

#!/bin/bash

IP=$1

ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o BatchMode=yes $IP exit &>/dev/null

if [ $? -ne 0 ]; then
    echo "SSH to ${IP} without password check failed"
    exit 1
fi

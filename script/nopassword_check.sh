#!/bin/bash

IP=$1
OUTPUT_DIR=$2

OUTPUT_FILE=${OUTPUT_DIR}/${IP}.no_password_check.result
if [ -f ${OUTPUT_FILE} ]; then
    rm -rf ${OUTPUT_FILE}
fi

ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o BatchMode=yes $IP exit > ${OUTPUT_FILE} 2>&1

if [ $? -ne 0 ]; then
    echo "SSH to ${IP} without password check failed" >> ${OUTPUT_FILE}
    exit 1
fi

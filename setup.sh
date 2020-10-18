#!/bin/bash

# scp necessary files to remote machine
IP=$1
TARGET_DIR=$2
OUTPUT_DIR=$3

OUTPUT_FILE=${OUTPUT_DIR}/${IP}.setup.result

# TODO:
ssh -o StrictHostKeyChecking=no $IP > ${OUTPUT_FILE} 2>/dev/null << remotessh
    exit
remotessh

if [ $? -eq 0 ]; then
    echo "SUCC" >> ${OUTPUT_FILE}
else
    echo "FAIL" >> ${OUTPUT_FILE}
fi

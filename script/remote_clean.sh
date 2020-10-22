#!/bin/bash

IP=$1
OUTPUT_DIR=$2
TARGET_DIR=$3

OUTPUT_FILE=${OUTPUT_DIR}/${IP}.clean.result
if [ -f ${OUTPUT_FILE} ]; then
    rm -rf ${OUTPUT_FILE}
fi

ssh $IP > ${OUTPUT_FILE} 2>&1 << remotessh

rm -rf ${TARGET_DIR}

remotessh

#!/bin/bash

# scp necessary files to remote machine

# For ucx_test:
# show_gid.sh  test_types_ucp
FILES=(show_gid.sh test_types_ucp)

IP=$1
OUTPUT_DIR=$2
TARGET_DIR=$3

for f in ${FILES[@]}
do 
    if [ ! -f $f ]; then
        echo "Cannot find $f here"
        exit 1
    fi
done

OUTPUT_FILE=${OUTPUT_DIR}/${IP}.setup.result
if [ -f $OUTPUT_FILE ]; then
    rm -rf $OUTPUT_FILE
fi

# create directory

ssh $IP << remotessh

# TODO: remove old directory?

mkdir -p ${TARGET_DIR}

remotessh


for f in ${FILES[@]}
do
    scp -p -o StrictHostKeyChecking=no $f root@$IP:${TARGET_DIR}/ >> ${OUTPUT_FILE} 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Scp for $f failed" >> ${OUTPUT_FILE} 
        echo "FAIL" >> ${OUTPUT_FILE}
        exit 1
    fi
done

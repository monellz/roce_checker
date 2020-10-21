#!/bin/bash

# IP1 as the client
# IP2 as the server
IP1=$1
IP2=$2
PORT=$3

OUTPUT_DIR=$4
TARGET_DIR=$5

OUTPUT_FILE=${OUTPUT_DIR}/${IP1}-${IP2}.ucx.result

if [ -f ${OUTPUT_FILE} ]; then
    rm -rf ${OUTPUT_FILE}
fi


# server side

ssh ${IP2} \
"cd ${TARGET_DIR};" \
"source env_load.sh ${IP2} ${TARGET_DIR};" \
'pkill ucx_perftest;' \
'export UCX_TLS=rc;' \
'export UCX_NET_DEVICES=${DEV}:${V2_PORT};' \
"ucx_perftest -b test_types_ucp -p ${PORT};" \
'exit' > /dev/null 2>&1 &

# client side

ssh ${IP1} > ${OUTPUT_FILE} 2>/dev/null << remotessh

cd ${TARGET_DIR}
source env_load.sh ${IP1} ${TARGET_DIR}

# try 3 times for connection
for i in {1..3}
do
    sleep 5
    ucx_perftest -p ${PORT} -b test_types_ucp ${IP2} 2>&1
    if [[ $? -eq 0 ]]; then
        exit 0
    fi
done

exit 1
remotessh

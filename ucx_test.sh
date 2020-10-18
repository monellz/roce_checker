#!/bin/bash

IP=$1
SERVER_IP=$2
OUTPUT_DIR=$3


OUTPUT_FILE=${OUTPUT_DIR}/${IP}-${SERVER_IP}.ucx.result

if [ -f ${OUTPUT_FILE} ]; then
    rm -rf ${OUTPUT_FILE}
fi


# server side

ssh root@${SERVER_IP} \
"cd ${OUTPUT_DIR};" \
"source env_load.sh ${SERVER_IP} ${OUTPUT_DIR};" \
'pkill ucx_perftest;' \
'export UCX_TLS=rc;' \
'export UCX_NET_DEVICES=${DEV}:${V2_PORT};' \
'ucx_perftest -b test_types_ucp;' \
'exit' > /dev/null 2>&1 &

# client side
# get device info
source env_load.sh ${IP} ${OUTPUT_DIR}

# try 3 times for connection
for i in {1..3}
do
    echo "Connection Round ${i}"
    sleep 5
    ucx_perftest -b test_types_ucp ${SERVER_IP} >> ${OUTPUT_FILE} 2>&1
    if [[ $? -eq 0 ]]; then
        break
    fi
done

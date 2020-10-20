#!/bin/bash

# IP1 as the client
# IP2 as the server
IP1=$1
IP2=$2

TARGET_DIR=$3
OUTPUT_DIR=$4

OUTPUT_FILE=${OUTPUT_DIR}/${IP1}-${IP2}.perf_v2.result

if [ -f ${OUTPUT_FILE} ]; then
    rm -rf ${OUTPUT_FILE}
fi

perfsuit=(RC UC UD)
transtype=(RC)

for case in ${perfsuit[@]}
do
    for type in ${transtype[@]}
    do
        if [ $type = "UC" ] && [[ $case =~ "read" ]]; then
            echo "UC connection not possible in READ/ATOMIC verbs"
            continue
        fi
        
        if [ $type = "UD" ] && ([[ $case =~ "read" ]] || [[ $case =~ "write" ]]); then
            echo "UD connection only possible in SEND verb"
            continue
        fi

        # DO TEST
        
        echo "$case transfer type $type V2 version"
        
        # server side
        ssh ${IP2} \
        "cd ${TARGET_DIR};" \
        "source env_load.sh ${IP2} ${TARGET_DIR};" \
        "inner_case=$case;" \
        "inner_type=$type;" \
        '$inner_case -x $V2_INDEX -d $DEV -c $inner_type --report_gbits;' \
        'exit' > /dev/null 2>&1 &
        
        
        # client side
        for i in {1..3}
        do
            sleep 5
            ssh ${IP1} \
            "cd ${TARGET_DIR};" \
            "source env_load.sh ${IP1} ${TARGET_DIR};" \
            "inner_case=$case;" \
            "inner_type=$type;" \
            "inner_serverip=$IP2;" \
            '$inner_case $inner_serverip --report_gbits -F -x $V2_INDEX -d $DEV -c $inner_type;" \
            'exit' > ${OUTPUT_FILE} 2>&1

            if [[ $? -eq 0 ]]; then
                exit 0
            fi
        done
    done
done



# server side

ssh ${IP2} \
"cd ${TARGET_DIR};" \
"source env_load.sh ${IP2} ${TARGET_DIR};" \
'pkill ucx_perftest;' \
'export UCX_TLS=rc;' \
'export UCX_NET_DEVICES=${DEV}:${V2_PORT};' \
'ucx_perftest -b test_types_ucp;' \
'exit' > /dev/null 2>&1 &

# client side

ssh ${IP1} > ${OUTPUT_FILE} 2>/dev/null << remotessh

cd ${TARGET_DIR}
source env_load.sh ${IP1} ${TARGET_DIR}

# try 3 times for connection
for i in {1..3}
do
    sleep 5
    ucx_perftest -b test_types_ucp ${IP2} 2>&1
    if [[ $? -eq 0 ]]; then
        exit 0
    fi
done

exit 1
remotessh

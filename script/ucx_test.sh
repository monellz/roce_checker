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




parse_ucx_result() {
    FILE=$1

    #perfsuit=(ucp_iov_contig_tag_lat ucp_iov_iov_tag_lat ucp_contig_contig_tag_lat ucp_iov_contig_tag_bw ucp_iov_iov_tag_bw ucp_contig_contig_tag_bw ucp_sync_tag_lat ucp_unexp_tag_lat ucp_wild_tag_lat ucp_stream_bw ucp_stream_lat ucp_put_lat ucp_put_bw ucp_get)
    perfsuit=(put_bw)

    for case in ${perfsuit[@]}
    do
        # test_types_ucp,iterations,typical_lat,avg_lat,overall_lat,avg_bw,overall_bw,avg_mr,overall_mr
        data=$(grep ${case} < ${FILE} | awk '{print $2}')
        echo ${case},${data}
        if [ -z "$data" ]; then
            echo "Parse Error for ${case}" >> ${OUTPUT_FILE}
            return 10
        fi
    done
    return 0
}


try_num=0
for i in {1..20}
do

# server side

    ssh ${IP2} \
    "cd ${TARGET_DIR};" \
    "source env_load.sh ${IP2} ${TARGET_DIR};" \
    'pkill ucx_perftest;' \
    'export UCX_TLS=rc;' \
    'export UCX_NET_DEVICES=${DEV}:${V2_PORT};' \
    "export inner_port=${PORT};" \
    'ucx_perftest -c 0 -x rc_verbs -d ${UCX_NET_DEVICES} -b test_types_ucp -s 8192 -D bcopy -p ${inner_port};' \
    'exit $?' > /dev/null 2>&1 &

    # server_ip=$!

    # trap "echo trap handling for term... >> ${OUTPUT_FILE};kill ${server_ip};exit" SIGTERM

    # client side


    ssh ${IP1} \
    'sleep 3;' \
    "cd ${TARGET_DIR};" \
    "source env_load.sh ${IP1} ${TARGET_DIR};" \
    'pkill ucx_perftest;' \
    'export UCX_TLS=rc;' \
    'export UCX_NET_DEVICES=${DEV}:${V2_PORT};' \
    "export inner_port=${PORT};" \
    "export inner_server_ip=${IP2};" \
    'ucx_perftest -c 0 -x rc_verbs -d ${UCX_NET_DEVICES} -b test_types_ucp -s 8192 -D bcopy -p ${inner_port} -f -v ${inner_server_ip};' \
    'exit $?' > ${OUTPUT_FILE} 2>&1

    if [[ $? -eq 0 ]]; then
        # get result from file, use stdout
        parse_ucx_result ${OUTPUT_FILE}
        if [[ $? -eq 0 ]]; then
            echo "try $i times" >> ${OUTPUT_FILE}
            echo "cmd: $0 $1 $2 $3 $4 $5" >> ${OUTPUT_FILE}
            exit 0
        fi
    else
        sleep 1
    fi
done

echo "Err try 20 times" >> ${OUTPUT_FILE}
echo "cmd: $0 $1 $2 $3 $4 $5" >> ${OUTPUT_FILE}
exit 1

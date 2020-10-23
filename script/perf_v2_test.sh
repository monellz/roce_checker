#!/bin/bash

# IP1 as the client
# IP2 as the server
IP1=$1
IP2=$2
PORT=$3

OUTPUT_DIR=$4
TARGET_DIR=$5

OUTPUT_FILE=${OUTPUT_DIR}/${IP1}-${IP2}.perf_v2.result

if [ -f ${OUTPUT_FILE} ]; then
    rm -rf ${OUTPUT_FILE}
fi

perfsuit=(ib_send_bw ib_send_lat)
transtype=(UD)

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
        
        #echo "$case transfer type $type V2 version" >> ${OUTPUT_FILE}
        echo "$case,$type,V2" >> ${OUTPUT_FILE}
        
        # server side
        ssh ${IP2} \
        "cd ${TARGET_DIR};" \
        "source env_load.sh ${IP2} ${TARGET_DIR};" \
        "inner_case=$case;" \
        "inner_type=$type;" \
        "inner_port=${PORT};" \
        '$inner_case -p $inner_port -x $V2_INDEX -d $DEV -c $inner_type --report_gbits;' \
        'exit $?' > /dev/null 2>&1 &


        server_ip=$!
        trap "echo trap handling for term... >> ${OUTPUT_FILE};kill ${server_ip};exit" SIGTERM

        
        # client side
        for i in {1..3}
        do
            sleep 3
            ssh ${IP1} \
            "cd ${TARGET_DIR};" \
            "source env_load.sh ${IP1} ${TARGET_DIR};" \
            "inner_case=$case;" \
            "inner_type=$type;" \
            "inner_serverip=$IP2;" \
            "inner_port=${PORT};" \
            '$inner_case $inner_serverip --report_gbits -F -p $inner_port -x $V2_INDEX -d $DEV -c $inner_type;' \
            'exit $?' >> ${OUTPUT_FILE} 2>&1

            if [[ $? -eq 0 ]]; then
                break
            fi
        done
    done
done

parse_perf_result() {
    FILE=$1
    perfsuit=(ib_send_bw ib_read_bw ib_write_bw ib_send_lat ib_read_lat ib_write_lat)
    for case in ${perfsuit[@]}
    do
        baseline=($( cat ${FILE} |grep -n $case |awk -F ":" '{print $1}'))
        for l in ${baseline[@]}
        do
            casename=$(sed -n ''$(($l))'p' ${FILE})
            tmp=$(mktemp)
            cat ${FILE} |grep -A 25 -E "$casename"|grep -A 2 "#bytes" > ${tmp}
            caseresult=$(sed -n '2p' ${tmp} | awk '{print ($4)}')
            rm -rf ${tmp}
            if [ ! $caseresult ]; then
                exit 1
            else
                echo $casename","$caseresult
            fi	
        done
    done
}

if [[ $? -eq 0 ]]; then
    # get result from file, use stdout
    parse_perf_result ${OUTPUT_FILE}
else
    exit 1
fi

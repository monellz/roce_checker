#!/bin/bash

IP1=$1
IP2=$2
OUTPUT_DIR=$3
OUTPUT_FILE=${OUTPUT_DIR}/${IP1}-${IP2}.connection_check.result


check_nopasswd_ssh() {
    echo "nopassswd"
    server_ip=$1
    ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o BatchMode=yes $server_ip exit &>/dev/null

    if [ $? -ne 0 ]; then
        echo "SSH to $server_ip without password check failed"
        exit 1
    fi
}

# TODO: bug
check_network() {
    echo "network"
    client_ip=$1
    server_ip=$2
    ipadd=$(ifconfig | grep $client_ip)
    if [[ -n "$ipadd" ]]; then
        echo "IP address config check failed" >>env.csv
        exit 1
    else
        pr=$(ping $server_ip -c 3 |grep "ping statistics")
        if [[ -z $pr ]]; then
            echo "IP address ping check failed"
            exit 1
        fi
    fi
}

# IP1 -> IP2

# TOOD: It's very strange that I cannot merge the two check into one remote command

#ssh -o StrictHostKeyChecking=no $IP1 > ${OUTPUT_FILE} 2>/dev/null << remotessh
#    $(typeset -f check_network)
#    check_network $IP1 $IP2
#    exit
#remotessh
#
#if [ $? -eq 0 ]; then
#    echo "SUCC" >> ${OUTPUT_FILE}
#else
#    echo "FAIL" >> ${OUTPUT_FILE}
#    exit 1
#fi

ssh -o StrictHostKeyChecking=no $IP1 >> ${OUTPUT_FILE} 2>/dev/null << remotessh
    $(typeset -f check_nopasswd_ssh)
    check_nopasswd_ssh $IP1 $IP2
    exit
remotessh

if [ $? -eq 0 ]; then
    echo "SUCC" >> ${OUTPUT_FILE}
else
    echo "FAIL" >> ${OUTPUT_FILE}
    exit 1
fi


#!/bin/bash

IP1=$1
IP2=$2
OUTPUT_DIR=$3
OUTPUT_FILE=${OUTPUT_DIR}/${IP1}-${IP2}.connection_check.result

if [ -f $OUTPUT_FILE ]; then
    rm -rf $OUTPUT_FILE
fi

check_nopasswd_ssh() {
    server_ip=$1
    ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o BatchMode=yes $server_ip exit &>/dev/null

    if [ $? -ne 0 ]; then
        echo "SSH to $server_ip without password check failed"
        exit 1
    else
        echo "SSH to $server_ip without password check pass"
    fi
}

# TODO: bug
check_network() {
    client_ip=$1
    server_ip=$2
    ipadd=$(ifconfig | grep $client_ip)
    if [ -z $ipadd ]; then
        echo "IP address config check failed"
        exit 1
    else
        echo "IP address config check pass"
        #pr=$(ping $server_ip -c 3 |grep "ping statistics")
        pr=$(ping $server_ip -c 3 | grep "received" | awk '{print $4}')
        if [[ $pr -ne 3 ]]; then
            echo "IP address ping check failed"
            exit 1
        else
            echo "IP address ping check pass"
        fi
    fi
}

# IP1 -> IP2

# TOOD: It's very strange that I cannot merge the two check into one remote command

ssh -o StrictHostKeyChecking=no $IP1 > ${OUTPUT_FILE} 2>/dev/null << remotessh
    $(typeset -f check_network)
    check_network $IP1 $IP2
    exit $?
remotessh

if [ $? -ne 0 ]; then
    exit 1
fi

ssh -o StrictHostKeyChecking=no $IP1 >> ${OUTPUT_FILE} 2>/dev/null << remotessh
    $(typeset -f check_nopasswd_ssh)
    $(typeset -f check_network)
    check_nopasswd_ssh $IP1 $IP2
    exit $?
remotessh
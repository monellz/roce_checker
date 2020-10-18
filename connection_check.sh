#!/bin/bash

IP=$1
SERVER_IP=$2


check_nopasswd_ssh() {
    ssh  -o StrictHostKeyChecking=no -o PasswordAuthentication=no -o BatchMode=yes $SERVER_IP exit &>/dev/null
    if [ $? -ne 0 ]; then
        echo "SSH without password check failed"
        exit 1
    fi
}

# TODO: bug
check_network(){
    ipadd=$(ifconfig | grep $IP)
    if [[ -n "$ipadd" ]]; then
        echo "IP address config check failed" >>env.csv
        exit 1
    else
        pr=$(ping $SERVER_IP -c 3 |grep "ping statistics")
        if [[ -z $pr ]]; then
            echo "IP address ping check failed"
            exit 1
        fi
    fi
}


check_nopasswd_ssh
check_network

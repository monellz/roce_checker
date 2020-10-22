#!/bin/bash

IP=$1
OUTPUT_DIR=$2

OUTPUT_FILE=${OUTPUT_DIR}/${IP}.env_check.result

if [ -f $OUTPUT_FILE ]; then
    rm -rf $OUTPUT_FILE
fi


check_kernel_version() {
    local kernel_version=""
    if [ "$(uname -a | grep "4.19.148+")" == "" ]; then
        echo "OS (`uname -a`) do not support"
        exit 1
    fi
}


check_roce_mpi_health() {
    if [ "$(rpm -qa | grep rdma-core-20)" == "" ]; then
        echo "Do not install rdma-core-20"
        exit 1
    fi
    
    which mpirun | grep mpi &>/dev/null
    if [ $? -ne 0 ]; then
        echo "Do not install ompi-4.0"
        exit 1
    fi
}

check_cpu_number() {
    num=$(lscpu | awk '/^CPU(\(s\))?:/{print $2}')
    if [ ! $num ]; then
        echo "CPU check failed"
        exit 1
    fi
}

check_memory() {
    mem=$(grep MemTotal /proc/meminfo)
    if [ ! "$mem" ]; then
        echo "Memory check failed"
        exit 1
    fi
}

check_hugepage_size() {
    pagesize=$(grep Hugepage /proc/meminfo | ask '{print $2}')
    if [ $pagesize != 2048 ]; then
        echo "Memory huagepage size check failed"
        exit 1
    fi
}


check_nvme_storage() {
    nvme_num=$(fdisk -l | grep nvme | wc -l)
    if [ $nvme_num == 0 ]; then
        echo "Nvme check failed(number is 0)"
        exit 1
    fi
}

check_ucx(){
    ucxm=$(ucx_info -v )
    if [[ ! $ucxm =~ "UCT version=1.9.0" ]]; then
        echo "UCX install check failed"
        exit 1 
    fi
}


ssh -o StrictHostKeyChecking=no $IP > ${OUTPUT_FILE} 2>/dev/null << remotessh
    $(typeset -f check_kernel_version)
    $(typeset -f check_roce_mpi_health)
    $(typeset -f check_cpu_number)
    $(typeset -f check_memory)
    $(typeset -f check_ucx)

    check_kernel_version
    check_roce_mpi_health
    check_cpu_number
    check_memory
    check_ucx

    exit
remotessh

if [ $? -eq 0 ]; then
    echo "SUCC" >> ${OUTPUT_FILE}
else
    echo "FAIL" >> ${OUTPUT_FILE}
    exit 1
fi

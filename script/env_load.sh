#!/bin/bash

# load env var if node.cfg exists
# otherwise create node.cfg then load it

IP=$1
OUTPUT_DIR=$2
NODE_CFG=${OUTPUT_DIR}/node.cfg
#echo "IP=${IP}" "OUTPUT_DIR=$OUTPUT_DIR"

# create node.cfg
TMP=$(mktemp -p ${OUTPUT_DIR})
bash ${OUTPUT_DIR}/show_gid.sh > ${TMP}
DEV=$(awk '$0 ~ /'${IP}'/&&/v2/{print ($1) }'  ${TMP})
V1_INDEX=$(awk '$0 ~ /'$IP'/&&/v1/{print ($3) } ' ${TMP})
V2_INDEX=$(awk '$0 ~ /'$IP'/&&/v2/{print ($3) } ' ${TMP})
V2_PORT=$(awk '$0 ~ /'$IP'/&&/v2/{print ($2) } ' ${TMP})
NET_DEV=$(awk '$0 ~ /'$IP'/&&/v2/{print ($7) } '  ${TMP})
echo export DEV=${DEV} >> ${NODE_CFG}
echo export V1_INDEX=${V1_INDEX} >> ${NODE_CFG}
echo export V2_INDEX=${V2_INDEX} >> ${NODE_CFG}
echo export V2_PORT=${V2_PORT} >> ${NODE_CFG}
echo export NET_DEV=${NET_DEV} >> ${NODE_CFG}

rm -rf ${TMP}

source ${NODE_CFG}


#!/bin/bash

IP=$1
TARGET_DIR=$2

ssh $IP << remotessh

rm -rf ${TARGET_DIR}

remotessh

#!/bin/bash
python3 rocectl.py stop
pids=($(ps -ef | grep roce | grep test | grep sh | grep -v "grep" | awk '{print $2}'))
for pid in ${pids[@]}
do
    kill $pid
done

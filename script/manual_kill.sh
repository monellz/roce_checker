#!/bin/bash
pids=($(ps -ef | grep roce | grep test | grep sh | grep -v "grep" | awk '{print $2}'))
for pid in ${pids[@]}
do
    kill $pid
done
pids=($(ps -ef | grep roce | grep check | grep sh | grep -v "grep" | awk '{print $2}'))
for pid in ${pids[@]}
do
    kill $pid
done

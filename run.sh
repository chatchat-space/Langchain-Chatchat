#!/bin/bash
for i in $(seq 0 71)
do
    nohup bash cli.sh start cli --gpus 72 --index ${i} --debug False --device_num 8 >logs/faiss_${i}.log 2>&1 &
    echo "start $i task done"
    sleep 1m
done
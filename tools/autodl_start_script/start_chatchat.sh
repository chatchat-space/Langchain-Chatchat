#!/bin/bash

conda run -n chatchat  --no-capture-output export CHATCHAT_ROOT=/root/chatchat-data && chatchat start -a > >(tee chatchat-output.log) 2>&1 &
PID=$!
echo "Started chatchat with PID $PID"

echo "Checking if output.log has content..."
while [ ! -s chatchat-output.log ]; do
  echo "Waiting for output to appear in chatchat-output.log..."
  sleep 1
done
while ! grep -q "URL: http://0.0.0.0:6006" chatchat-output.log; do
        sleep 1
done


echo $PID > chatchat.pid
echo "chatchat started"



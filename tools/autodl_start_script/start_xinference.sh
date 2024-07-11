#!/bin/bash

conda run -n xinference  --no-capture-output xinference-local > >(tee xinference-output.log) 2>&1 &
PID=$!
echo "Started xinference-local with PID $PID"

echo "Checking if output.log has content..."
while [ ! -s xinference-output.log ]; do
  echo "Waiting for output to appear in xinference-output.log..."
  sleep 1
done
while ! grep -q "Uvicorn running on http://127.0.0.1:9997" xinference-output.log; do
      	sleep 1
done
echo "xinference-local started successfully"


bash /root/start_models.sh
bash /root/start_models_emb.sh


echo "Started xinference-local with PID $PID"

echo $PID > xinference.pid
echo "model started successfully"


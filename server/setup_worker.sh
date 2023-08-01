nohup python3 -m fastchat.serve.model_worker \
--model-name 'chatglm2-6b' \
--model-path THUDM/chatglm2-6b \
--num-gpus 2 \
>> ../logs/worker.log 2>&1 &

while [ `grep -c "Uvicorn running on" ../logs/worker.log` -eq '0' ];do
        sleep 3s;
        echo "wait worker running"
done
echo "worker running"
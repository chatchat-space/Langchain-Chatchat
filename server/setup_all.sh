[ -d "../logs/" ] && echo "log dir exists" || mkdir "../logs/"
# controller
nohup python3 -m fastchat.serve.controller >../logs/controller.log 2>&1 &
while [ `grep -c "Uvicorn running on" ../logs/controller.log` -eq '0' ];do
        sleep 1s;
        echo "wait controller running"
done
echo "controller running"

# worker
nohup python3 -m fastchat.serve.model_worker \
--model-name 'chatglm2-6b' \
--model-path THUDM/chatglm2-6b \
--num-gpus 2 \
>> ./logs/worker.log 2>&1 &

while [ `grep -c "Uvicorn running on" ../logs/worker.log` -eq '0' ];do
        sleep 3s;
        echo "wait worker running"
done
echo "worker running"

# webui
nohup python3 -m fastchat.serve.openai_api_server >> "../logs/openai_server.log" 2>&1 &

while [ `grep -c "Uvicorn running on" ../logs/openai_server.log` -eq '0' ];do
        sleep 3s;
        echo "wait openai_server running"
done
echo "openai_server running"
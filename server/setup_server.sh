# webui
nohup python3 -m fastchat.serve.openai_api_server >> "../logs/openai_server.log" 2>&1 &

while [ `grep -c "Uvicorn running on" ../logs/openai_server.log` -eq '0' ];do
        sleep 3s;
        echo "wait openai_server running"
done
echo "openai_server running"
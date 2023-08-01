# controller
nohup python3 -m fastchat.serve.controller >../logs/controller.log 2>&1 &
while [ `grep -c "Uvicorn running on" ../logs/controller.log` -eq '0' ];do
        sleep 1s;
        echo "wait controller running"
done
echo "controller running"
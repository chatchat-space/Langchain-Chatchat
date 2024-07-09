#!/bin/bash

rm -rf xinference-output.log
rm -rf chatchat-output.log

XINF_PID=xinference.pid
CHATCHAT_PID=chatchat.pid


echo "xinf stat"
kill `cat $XINF_PID`
rm -rf $XINF_PID

sleep 2
xinference_P_ID=`ps -ef | grep -w "xinference" | grep -v "grep" | awk '{print $2}'`
if [ "$xinference_P_ID" == "" ]; then
    echo "=== xinference process not exists or stop success"
else
    echo "=== xinference process pid is:$xinference_P_ID"
    echo "=== begin kill xinference process, pid is:$xinference_P_ID"
    kill -9 $xinference_P_ID
fi

echo "chatchat stat"
kill `cat $CHATCHAT_PID`
rm -rf $CHATCHAT_PID

sleep 1
chatchat_P_ID=`ps -ef | grep -w "chatchat" | grep -v "grep" | awk '{print $2}'`
if [ "$chatchat_P_ID" == "" ]; then
    echo "=== chatchat process not exists or stop success"
else
    echo "=== chatchat process pid is:$chatchat_P_ID"
    echo "=== begin kill chatchat process, pid is:$chatchat_P_ID"
    kill -9 $chatchat_P_ID
fi




bash /root/download_model.sh

bash /root/start_xinference.sh 

bash /root/start_chatchat.sh 





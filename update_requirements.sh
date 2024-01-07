#!/bin/bash

python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

while read requirement; do
    python -m pip install --upgrade "$requirement" -i https://pypi.tuna.tsinghua.edu.cn/simple
done < requirements.txt

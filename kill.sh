#!/bin/bash
ps -fe | grep python  | awk '{print $2}'  | xargs kill -9
rm -fr /home/zh.wang/chatglm_llm_fintech_raw_dataset/knowledge_base/tmp/*
rm -fr ./logs/*
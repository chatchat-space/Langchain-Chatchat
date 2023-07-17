#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@DOC : 测试接口并发性
@Date ：2023/7/17 15:25 
"""

import requests
import time
import concurrent.futures

inputBody = {
    "knowledge_base_id": None,
    "question": "写一个python语言实现的二叉树demo",
    # "question": "介绍一下自己?",
    "history": []
}
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


def send_request(url):
    t1 = time.time()
    print("start:", url)
    response = requests.post(url, json=inputBody, headers=headers)
    t2 = time.time()
    print("Time taken:", t2 - t1)
    print("end:", url)
    return response.text


url = 'http://localhost:7861/chat'
# host = 'localhost:7861/local_doc_qa/bing_search_chat'


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(send_request, url) for _ in range(5)]
    for future in concurrent.futures.as_completed(futures):
        response = future.result()
        print("Response:", response)

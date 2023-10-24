# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import pickle
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from params import *
import time
import requests
import urllib
import json

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa


    def upload(self):
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        # 如果../knowledge_base/keyphrases.pkl存在，则读取热词
        # 当前文件的父级目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        path = os.path.join(parent_dir,"knowledge_base/keyphrases.pkl")
        if os.path.exists(path):
            # 从文件中反序列化 keyphrases
            with open(path, "rb") as f:
                keyphrases = pickle.load(f)
            param_dict['hotWord'] = keyphrases
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url =lfasr_host + api_upload+"?"+urllib.parse.urlencode(param_dict),
                                headers = {"Content-type":"application/json"},data=data)
        print("upload_url:",response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result


    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['resultType'] = "transfer,predict"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result['content']['orderInfo']['status']
            print("status=",status)
            if status == 4:
                break
            time.sleep(5)
        print("get_result resp:",result)
        return result

def get_transcript_from_lattice(text):
    # 加载JSON数据
    data = json.loads(text)

    # 初始化空列表来存储识别的单词
    sentences = []

    # 遍历每个json_1best
    for item in data["lattice"]:
        # 加载json_1best的内容
        json_1best_data = json.loads(item["json_1best"])

        # 获取识别结果
        words = json_1best_data["st"]["rt"][0]["ws"]

        # 提取每个识别结果的单词
        sentence = ''.join([word["cw"][0]["w"] for word in words])
        
        # 添加到句子列表中
        sentences.append(sentence)

    # 将句子列表连接成一个字符串
    return ' '.join(sentences)



# 输入讯飞开放平台的appid，secret_key和待转写的文件路径
if __name__ == '__main__':
    api = RequestApi(appid="00853967",
                     secret_key="4fcabeb7dbc584a4c80f180d96a2be84",
                     upload_file_path=r"/data1/fga/Langchain-Chatchat/knowledge_base/Audio/content/中航资本大厦 6.m4a")

    result = api.get_result()
    text = get_transcript_from_lattice(result['content']['orderResult'])

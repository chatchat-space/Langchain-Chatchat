# import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import requests
import json
import time
import hashlib
from server.model_workers.base import ApiModelWorker
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal
from configs import TEMPERATURE


def calculate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    encrypted = md5.hexdigest()
    return encrypted


def do_request():
    url = "https://api.baichuan-ai.com/v1/stream/chat"
    api_key = ""
    secret_key = ""

    data = {
        "model": "Baichuan2-53B",
        "messages": [
            {
                "role": "user",
                "content": "世界第一高峰是"
            }
        ],
        "parameters": {
                    "temperature": 0.1,
                    "top_k": 10
                    }
    }

    json_data = json.dumps(data)
    time_stamp = int(time.time())
    signature = calculate_md5(secret_key + json_data + str(time_stamp))

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
        "X-BC-Request-Id": "your requestId",
        "X-BC-Timestamp": str(time_stamp),
        "X-BC-Signature": signature,
        "X-BC-Sign-Algo": "MD5",
    }

    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code == 200:
        print("请求成功！")
        print("响应header:", response.headers)
        print("响应body:", response.text)
    else:
        print("请求失败，状态码:", response.status_code)


class BaiChuanWorker(ApiModelWorker):
    BASE_URL = "https://api.baichuan-ai.com/v1/chat"
    SUPPORT_MODELS = ["Baichuan2-53B"]

    def __init__(
        self,
        *,
        controller_addr: str,
        worker_addr: str,
        model_names: List[str] = ["baichuan-api"],
        version: Literal["Baichuan2-53B"] = "Baichuan2-53B",
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 32768)
        super().__init__(**kwargs)

        # TODO: 确认模板是否需要修改
        self.conv = conv.Conversation(
            name=self.model_names[0],
            system_message="",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )

        config = self.get_config()
        self.version = config.get("version",version)
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")

    def generate_stream_gate(self, params):
        data = {
            "model": self.version,
            "messages": [
                {
                "role": "user",
                "content": params["prompt"]
                }
            ],
            "parameters": {
                "temperature": params.get("temperature",TEMPERATURE),
                "top_k": params.get("top_k",1)
            }
        }

        json_data = json.dumps(data)
        time_stamp = int(time.time())
        signature = calculate_md5(self.secret_key + json_data + str(time_stamp))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
            "X-BC-Request-Id": "your requestId",
            "X-BC-Timestamp": str(time_stamp),
            "X-BC-Signature": signature,
            "X-BC-Sign-Algo": "MD5",
        }

        response = requests.post(self.BASE_URL, data=json_data, headers=headers)

        if response.status_code == 200:
            resp = eval(response.text)
            yield json.dumps(
                {
                "error_code": resp["code"],
                "text": resp["data"]["messages"][-1]["content"]
                },
                ensure_ascii=False
            ).encode() + b"\0"
        else:
            yield json.dumps(
                {
                "error_code": resp["code"],
                "text": resp["msg"]
                },
                ensure_ascii=False
            ).encode() + b"\0"


    
    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)

if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = BaiChuanWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21001)
    # do_request()
import json
import time
import hashlib
import requests
from fastchat.conversation import Conversation
from server.model_workers.base import *
from server.utils import get_httpx_client
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal, Dict
from configs import logger, log_verbose

def calculate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    encrypted = md5.hexdigest()
    return encrypted


class BaiChuanWorker(ApiModelWorker):
    def __init__(
        self,
        *,
        controller_addr: str = None,
        worker_addr: str = None,
        model_names: List[str] = ["baichuan-api"],
        version: Literal["Baichuan2-53B"] = "Baichuan2-53B",
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 32768)
        super().__init__(**kwargs)
        self.version = version
    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])

        url = "https://api.baichuan-ai.com/v1/chat/completions"
        data = {
            "model": params.version,
            "messages": params.messages,
            "stream": False,
    
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + params.api_key,
           
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("请求成功！"+response.text)
            result = json.loads(response.text)
            textMsg=""
            result["choices"][0]["delta"]=result["choices"][0]["message"]
            if 'choices' in result:
                textMsg += result["choices"][0]["message"]["content"]
            data = {
                            "error_code": response.status_code,
                            "text": textMsg,
                            "choices":result["choices"],
                            "model":result["model"],
                            "object":result["object"],
                            "object":result["object"],
                            "created":result["created"],
                            "id":result["id"],
                            }
            
            yield data

        else:
             
             data = {
                            "error_code": response.status_code,
                            "text":response.text,
                            "error": {
                                "message": response.text,
                                "type": "invalid_request_error",
                                "param": None,
                                "code": None,
                            }
                    }
             self.logger.error(f"请求百川 API 时发生错误：{data}")
             yield data
    def get_embeddings(self, params):
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = BaiChuanWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21007",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21007)
    # do_request()

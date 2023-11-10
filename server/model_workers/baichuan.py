# import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import json
import time
import hashlib
from server.model_workers.base import ApiModelWorker
from server.utils import get_model_worker_config, get_httpx_client
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal, Dict
from configs import TEMPERATURE


def calculate_md5(input_string):
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    encrypted = md5.hexdigest()
    return encrypted


def request_baichuan_api(
    messages: List[Dict[str, str]],
    api_key: str = None,
    secret_key: str = None,
    version: str = "Baichuan2-53B",
    temperature: float = TEMPERATURE,
    model_name: str = "baichuan-api",
):
    config = get_model_worker_config(model_name)
    api_key = api_key or config.get("api_key")
    secret_key = secret_key or config.get("secret_key")
    version = version or config.get("version")

    url = "https://api.baichuan-ai.com/v1/stream/chat"
    data = {
        "model": version,
        "messages": messages,
        "parameters": {"temperature": temperature}
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

    with get_httpx_client() as client:
        with client.stream("POST", url, headers=headers, json=data) as response:
            for line in response.iter_lines():
                if not line.strip():
                    continue
                resp = json.loads(line)
                yield resp


class BaiChuanWorker(ApiModelWorker):
    BASE_URL = "https://api.baichuan-ai.com/v1/stream/chat"
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
        super().generate_stream_gate(params)

        messages = self.prompt_to_messages(params["prompt"])

        text = ""
        for resp in request_baichuan_api(messages=messages,
                                          api_key=self.api_key,
                                          secret_key=self.secret_key,
                                          version=self.version,
                                          temperature=params.get("temperature")):
            if resp["code"] == 0:
                text += resp["data"]["messages"][-1]["content"]
                yield json.dumps(
                    {
                    "error_code": resp["code"],
                    "text": text
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
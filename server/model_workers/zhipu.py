from fastchat.conversation import Conversation
from server.model_workers.base import *
from fastchat import conversation as conv
import sys
from typing import List, Dict, Iterator, Literal
from configs import logger, log_verbose
import requests
import jwt
import time
import json


def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


class ChatGLMWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            model_names: List[str] = ["zhipu-api"],
            controller_addr: str = None,
            worker_addr: str = None,
            version: Literal["chatglm_turbo"] = "chatglm_turbo",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 4096)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Iterator[Dict]:
        params.load_config(self.model_names[0])
        token = generate_token(params.api_key, 60)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "model": params.version,
            "messages": params.messages,
            "max_tokens": params.max_tokens,
            "temperature": params.temperature,
            "stream": False
        }
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        response = requests.post(url, headers=headers, json=data)
        # for chunk in response.iter_lines():
        #     if chunk:
        #         chunk_str = chunk.decode('utf-8')
        #         json_start_pos = chunk_str.find('{"id"')
        #         if json_start_pos != -1:
        #             json_str = chunk_str[json_start_pos:]
        #             json_data = json.loads(json_str)
        #             for choice in json_data.get('choices', []):
        #                 delta = choice.get('delta', {})
        #                 content = delta.get('content', '')
        #                 yield {"error_code": 0, "text": content}
        ans = response.json()
        content = ans["choices"][0]["message"]["content"]
        yield {"error_code": 0, "text": content}

    def get_embeddings(self, params):
        # 临时解决方案，不支持embedding
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是智谱AI小助手，请根据用户的提示来完成任务",
            messages=[],
            roles=["user", "assistant", "system"],
            sep="\n###",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = ChatGLMWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21001)

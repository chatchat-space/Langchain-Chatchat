from contextlib import contextmanager
import httpx
from fastchat.conversation import Conversation
from httpx_sse import EventSource
from server.model_workers.base import *
from fastchat import conversation as conv
import sys
from typing import List, Dict, Iterator, Literal, Any
import jwt
import time
import uuid
import requests
from .auth_util import gen_sign_headers

@contextmanager
def connect_sse(client: httpx.Client, method: str, url: str, **kwargs: Any):
    with client.stream(method, url, **kwargs) as response:
        yield EventSource(response)


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


class LANXINWorker(ApiModelWorker):
    DEFAULT_EMBED_MODEL = "embedding-2"
    
    def __init__(
            self,
            *,
            model_names: List[str] = ["vivo-api"],
            controller_addr: str = None,
            worker_addr: str = None,
            version: Literal["glm-4"] = "glm-4",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 4096)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Iterator[Dict]:
        params.load_config(self.model_names[0])
        params_uid = {'requestId': str(uuid.uuid4())}

        data = {
            'messages': params.messages,
            'model': 'vivo-BlueLM-TB',
            'sessionId': str(uuid.uuid4()),
            'systemPrompt': '',
            'extra': {
                'temperature': 0.9
            }
        }

        URI = '/vivogpt/completions'
        DOMAIN = 'api-ai.vivo.com.cn'
        headers = gen_sign_headers("3030031671", "OPAMHkbbsByTDAks", 'POST', URI, params_uid)
        url = 'https://{}{}'.format(DOMAIN, URI)

        response = requests.post(url, json=data, headers=headers, params=params_uid)

        if response.status_code == 200:
            res_obj = response.json()
            print(f'response:{res_obj}')
            if res_obj['code'] == 0 and res_obj.get('data'):
                content = res_obj['data']['content']
        else:
            print(response.status_code, response.text)
        yield {"error_code": 0, "text": content}

    def get_embeddings(self, params):
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

    worker = LANXINWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21001)

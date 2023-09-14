from server.model_workers.base import ApiModelWorker
from configs.model_config import TEMPERATURE
from fastchat import conversation as conv
import sys
import json
import httpx
from cachetools import cached, TTLCache
from server.utils import get_model_worker_config
from typing import List, Literal, Dict


# TODO: support all qianfan models
MODEL_VERSIONS = {
    "ernie-bot": "completions",
    "ernie-bot-turbo": "eb-instant",
}


@cached(TTLCache(1, 1800)) # 经过测试，缓存的token可以使用，目前每30分钟刷新一次
def get_baidu_access_token(api_key: str, secret_key: str) -> str:
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    try:
        return httpx.get(url, params=params).json().get("access_token")
    except Exception as e:
        print(f"failed to get token from baidu: {e}")


def request_qianfan_api(
    messages: List[Dict[str, str]],
    temperature: float = TEMPERATURE,
    model_name: str = "qianfan-api",
    version: str = None,
) -> Dict:
    BASE_URL = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat'\
               '/{model_version}?access_token={access_token}'
    config = get_model_worker_config(model_name)
    version = version or config.get("version")
    access_token = get_baidu_access_token(config.get("api_key"), config.get("secret_key"))
    if not access_token:
        raise RuntimeError(f"failed to get access token. have you set the correct api_key and secret key?")

    url = BASE_URL.format(
        model_version=MODEL_VERSIONS[version],
        access_token=access_token,
    )
    payload = {
        "messages": messages,
        "temperature": temperature,
        "stream": True
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    with httpx.stream("POST", url, headers=headers, json=payload) as response:
        for line in response.iter_lines():
            if not line.strip():
                continue
            if line.startswith("data: "):
                line = line[6:]
            resp = json.loads(line)
            yield resp


class QianFanWorker(ApiModelWorker):
    """
    百度千帆
    """
    def __init__(
            self,
            *,
            version: Literal["ernie-bot", "ernie-bot-turbo"] = "ernie-bot",
            model_names: List[str] = ["ernie-api"],
            controller_addr: str,
            worker_addr: str,
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384)
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
        self.version = version
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")

    def generate_stream_gate(self, params):
        messages = self.prompt_to_messages(params["prompt"])
        text=""
        for resp in request_qianfan_api(messages,
                                        temperature=params.get("temperature"),
                                        model_name=self.model_names[0]):
            if "result" in resp.keys():
                text += resp["result"]
                yield json.dumps({
                    "error_code": 0,
                    "text": text
                },
                    ensure_ascii=False
                ).encode() + b"\0"
            else:
                yield json.dumps({
                    "error_code": resp["error_code"],
                    "text": resp["error_msg"]
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

    worker = QianFanWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:20006",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20006)
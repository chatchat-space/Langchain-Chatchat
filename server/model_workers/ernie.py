from server.model_workers.base import ApiModelWorker
from fastchat import conversation as conv
import sys
import json
import requests
from typing import List, Literal

MODEL_VERSIONS = {
    "ernie-bot": "completions",
    "ernie-bot-turbo": "eb-instant"
}


class ErnieWorker(ApiModelWorker):
    """
    百度 Ernie
    """
    BASE_URL = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat'\
               '/{model_version}?access_token={access_token}'
    SUPPORT_MODELS = list(MODEL_VERSIONS.keys())

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
        self.access_token = self.get_access_token()

    def get_access_token(self):
        """
        使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
        """

        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials"\
              f"&client_id={self.api_key}"\
              f"&client_secret={self.secret_key}"

        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json().get("access_token")

    def generate_stream_gate(self, params):
        url = self.BASE_URL.format(
            model_version=MODEL_VERSIONS[self.version],
            access_token=self.access_token
        )
        payload = json.dumps({
            "messages": self.prompt_to_messages(params["prompt"]),
            "stream": True
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, stream=True)

        text=""
        for line in response.iter_lines():
            if line.decode("utf-8").startswith("data: "):  # 真是优秀的返回
                resp = json.loads(line.decode("utf-8")[6:])
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

    worker = EnrieWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:20003",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20003)
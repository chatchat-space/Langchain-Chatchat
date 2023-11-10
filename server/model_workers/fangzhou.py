from server.model_workers.base import ApiModelWorker
from configs.model_config import TEMPERATURE
from fastchat import conversation as conv
import sys
import json
from pprint import pprint
from server.utils import get_model_worker_config
from typing import List, Literal, Dict


def request_volc_api(
    messages: List[Dict],
    model_name: str = "fangzhou-api",
    version: str = "chatglm-6b-model",
    temperature: float = TEMPERATURE,
    api_key: str = None,
    secret_key: str = None,
):
    from volcengine.maas import MaasService, MaasException, ChatRole

    maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
    config = get_model_worker_config(model_name)
    version = version or config.get("version")
    version_url = config.get("version_url")
    api_key = api_key or config.get("api_key")
    secret_key = secret_key or config.get("secret_key")

    maas.set_ak(api_key)
    maas.set_sk(secret_key)

    # document: "https://www.volcengine.com/docs/82379/1099475"
    req = {
        "model": {
            "name": version,
        },
        "parameters": {
            # 这里的参数仅为示例，具体可用的参数请参考具体模型的 API 说明
            "max_new_tokens": 1000,
            "temperature": temperature,
        },
        "messages": messages,
    }

    try:
        resps = maas.stream_chat(req)
        for resp in resps:
            yield resp
    except MaasException as e:
        print(e)


class FangZhouWorker(ApiModelWorker):
    """
    火山方舟
    """
    SUPPORT_MODELS = ["chatglm-6b-model"]

    def __init__(
            self,
            *,
            version: Literal["chatglm-6b-model"] = "chatglm-6b-model",
            model_names: List[str] = ["fangzhou-api"],
            controller_addr: str,
            worker_addr: str,
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384) # TODO: 不同的模型有不同的大小

        super().__init__(**kwargs)

        config = self.get_config()
        self.version = version
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")

        self.conv = conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明、对人类有帮助的人工智能，你可以对人类提出的问题给出有用、详细、礼貌的回答。",
            messages=[],
            roles=["user", "assistant", "system"],
            sep="\n### ",
            stop_str="###",
        )

    def generate_stream_gate(self, params):
        super().generate_stream_gate(params)

        messages = self.prompt_to_messages(params["prompt"])
        text = ""

        for resp in request_volc_api(messages=messages,
                                    model_name=self.model_names[0],
                                    version=self.version,
                                    temperature=params.get("temperature", TEMPERATURE),
                                    ):
            error = resp.error
            if error.code_n > 0:
                data = {"error_code": error.code_n, "text": error.message}
            elif chunk := resp.choice.message.content:
                text += chunk
                data = {"error_code": 0, "text": text}
            yield json.dumps(data, ensure_ascii=False).encode() + b"\0"

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = FangZhouWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21005",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21005)

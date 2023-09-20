import json
import sys
from configs import TEMPERATURE
from http import HTTPStatus
from typing import List, Literal, Dict

from fastchat import conversation as conv

from server.model_workers.base import ApiModelWorker
from server.utils import get_model_worker_config


def request_qwen_api(
    messages: List[Dict[str, str]],
    api_key: str = None,
    version: str = "qwen-turbo",
    temperature: float = TEMPERATURE,
    model_name: str = "qwen-api",
):
    import dashscope

    config = get_model_worker_config(model_name)
    api_key = api_key or config.get("api_key")
    version = version or config.get("version")

    gen = dashscope.Generation()
    responses = gen.call(
        model=version,
        temperature=temperature,
        api_key=api_key,
        messages=messages,
        result_format='message',  # set the result is message format.
        stream=True,
    )

    text = ""
    for resp in responses:
        if resp.status_code != HTTPStatus.OK:
            yield {
                "code": resp.status_code,
                "text": "api not response correctly",
            }

        if resp["status_code"] == 200:
            if choices := resp["output"]["choices"]:
                yield {
                    "code": 200,
                    "text": choices[0]["message"]["content"],
                }
        else:
            yield {
                "code": resp["status_code"],
                "text": resp["message"],
            }


class QwenWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            version: Literal["qwen-turbo", "qwen-plus"] = "qwen-turbo",
            model_names: List[str] = ["qwen-api"],
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
            system_message="你是一个聪明、对人类有帮助的人工智能，你可以对人类提出的问题给出有用、详细、礼貌的回答。",
            messages=[],
            roles=["user", "assistant", "system"],
            sep="\n### ",
            stop_str="###",
        )
        config = self.get_config()
        self.api_key = config.get("api_key")
        self.version = version

    def generate_stream_gate(self, params):
        messages = self.prompt_to_messages(params["prompt"])

        for resp in request_qwen_api(messages=messages,
                                     api_key=self.api_key,
                                     version=self.version,
                                     temperature=params.get("temperature")):
            if resp["code"] == 200:
                yield json.dumps({
                    "error_code": 0,
                    "text": resp["text"]
                },
                    ensure_ascii=False
                ).encode() + b"\0"
            else:
                yield json.dumps({
                    "error_code": resp["code"],
                    "text": resp["text"]
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

    worker = QwenWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:20007",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20007)

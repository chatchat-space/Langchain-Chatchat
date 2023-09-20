import json
import sys
from http import HTTPStatus
from typing import List, Literal

from fastchat import conversation as conv

from server.model_workers.base import ApiModelWorker


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
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )
        config = self.get_config()
        self.api_key = config.get("api_key")
        self.version = version

    def generate_stream_gate(self, params):
        import dashscope

        text = ""
        gen = dashscope.Generation()
        responses = gen.call(
            model=self.version,
            api_key=self.api_key,
            prompt=params["prompt"],
            result_format='message',  # set the result is message format.
            stream=True,
        )
        for resp in responses:
            if resp.status_code == HTTPStatus.OK:
                for choice in resp["output"]["choices"]:
                    text = choice["message"]["content"]
                yield json.dumps({
                    "error_code": 0,
                    "text": text
                },
                    ensure_ascii=False
                ).encode() + b"\0"
            else:
                yield json.dumps({
                    "error_code": 0,
                    "text": resp["message"]
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

from server.model_workers.base import ApiModelWorker
from configs.model_config import TEMPERATURE
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal, Dict


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
        kwargs.setdefault("context_len", 16384)
        super().__init__(**kwargs)

        config = self.get_config()
        self.version = version
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")

        from volcengine.maas import ChatRole
        self.conv = conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明、对人类有帮助的人工智能，你可以对人类提出的问题给出有用、详细、礼貌的回答。",
            messages=[],
            roles=[ChatRole.USER, ChatRole.ASSISTANT, ChatRole.SYSTEM],
            sep="\n### ",
            stop_str="###",
        )

    def generate_stream_gate(self, params):
        super().generate_stream_gate(params)
        from volcengine.maas import MaasService, MaasException, ChatRole
        maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')

        maas.set_ak(self.api_key)
        maas.set_sk(self.secret_key)

        # document: "https://www.volcengine.com/docs/82379/1099475"
        req = {
            "model": {
                "name": self.version,
            },
            "parameters": {
                # 这里的参数仅为示例，具体可用的参数请参考具体模型的 API 说明
                # "max_new_tokens": 1000,
                "temperature": params.get("temperature", TEMPERATURE),
            },
            "messages": [{"role": ChatRole.USER, "content": params["prompt"]}]
        }
        text = ""
        try:

            resps = maas.stream_chat(req)
            for resp in resps:
                text += resp.choice.message.content
                yield json.dumps({"error_code": 0, "text": text},
                                 ensure_ascii=False).encode() + b"\0"
        except MaasException as e:
            print(e)


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
        worker_addr="http://127.0.0.1:20006",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20006)

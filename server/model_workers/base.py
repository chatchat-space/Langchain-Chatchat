from fastchat.serve.model_worker import BaseModelWorker
import uuid
import json
from pydantic import BaseModel
from typing import Dict, List


class ConvTemplate(BaseModel):
    name: str = "chatglm-api"
    system_template: str = "{system_message}"
    system_message: str = ""
    roles: List[str] = [] # ["问", "答"]
    messages: List = []
    offset: int = 0
    sep_style: int =8
    sep: str = "\n\n"
    sep2: str = None
    stop_str: str = None,
    stop_token_ids: str = None


def get_conv_template(conv_template):
    return ConvTemplate()


def get_conversation_template(model_path):
    return ConvTemplate()


class ApiModelWorker(BaseModelWorker):
    BASE_URL: str
    SUPPORT_MODELS: List

    def __init__(self, model_name: str, context_len: int = 2048, **kwargs):
        kwargs.setdefault("worker_id", uuid.uuid4().hex[:8])
        kwargs.setdefault("model_path", "")
        kwargs.setdefault("model_names", [model_name])
        kwargs.setdefault("limit_worker_concurrency", 5)
        super().__init__(**kwargs)
        self.context_len = context_len
        self.init_heart_beat()

    def count_token(self, params):
        print("count token")
        print(params)
        prompt = params["prompt"]
        return {"count": len(str(prompt)), "error_code": 0}

    def generate_stream_gate(self, params):
        print("stream")
        print(params)
        self.call_ct += 1
    
    def generate_gate(self, params):
        # TODO: 需要根据实际进行调整
        text = ""
        for x in self.generate_stream_gate(params):
            text += x
        return text

    def get_embeddings(self, params):
        print("embedding")
        print(params)

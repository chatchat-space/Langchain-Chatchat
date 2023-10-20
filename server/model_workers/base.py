from configs.basic_config import LOG_PATH
import fastchat.constants
fastchat.constants.LOGDIR = LOG_PATH
from fastchat.serve.base_model_worker import BaseModelWorker
import uuid
import json
import sys
from pydantic import BaseModel
import fastchat
import asyncio
from typing import Dict, List


# 恢复被fastchat覆盖的标准输出
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__


class ApiModelOutMsg(BaseModel):
    error_code: int = 0
    text: str

class ApiModelWorker(BaseModelWorker):
    BASE_URL: str
    SUPPORT_MODELS: List

    def __init__(
        self,
        model_names: List[str],
        controller_addr: str,
        worker_addr: str,
        context_len: int = 2048,
        **kwargs,
    ):
        kwargs.setdefault("worker_id", uuid.uuid4().hex[:8])
        kwargs.setdefault("model_path", "")
        kwargs.setdefault("limit_worker_concurrency", 5)
        super().__init__(model_names=model_names,
                        controller_addr=controller_addr,
                        worker_addr=worker_addr,
                        **kwargs)
        self.context_len = context_len
        self.semaphore = asyncio.Semaphore(self.limit_worker_concurrency)
        self.init_heart_beat()

    def count_token(self, params):
        # TODO：需要完善
        # print("count token")
        prompt = params["prompt"]
        return {"count": len(str(prompt)), "error_code": 0}

    def generate_stream_gate(self, params):
        self.call_ct += 1
    
    def generate_gate(self, params):
        for x in self.generate_stream_gate(params):
            pass
        return json.loads(x[:-1].decode())

    def get_embeddings(self, params):
        print("embedding")
        # print(params)

    # help methods
    def get_config(self):
        from server.utils import get_model_worker_config
        return get_model_worker_config(self.model_names[0])

    def prompt_to_messages(self, prompt: str) -> List[Dict]:
        '''
        将prompt字符串拆分成messages.
        '''
        result = []
        user_role = self.conv.roles[0]
        ai_role = self.conv.roles[1]
        user_start = user_role + ":"
        ai_start = ai_role + ":"
        for msg in prompt.split(self.conv.sep)[1:-1]:
            if msg.startswith(user_start):
                if content := msg[len(user_start):].strip():
                    result.append({"role": user_role, "content": content})
            elif msg.startswith(ai_start):
                if content := msg[len(ai_start):].strip():
                    result.append({"role": ai_role, "content": content})
            else:
                raise RuntimeError(f"unknown role in msg: {msg}")
        return result

from configs.model_config import LOG_PATH
import fastchat.constants
fastchat.constants.LOGDIR = LOG_PATH
from fastchat.serve.model_worker import BaseModelWorker
import uuid
import json
import sys
from pydantic import BaseModel
import fastchat
import threading
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
        self.init_heart_beat()

    def count_token(self, params):
        # TODO：需要完善
        print("count token")
        print(params)
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
        print(params)

    # workaround to make program exit with Ctrl+c
    # it should be deleted after pr is merged by fastchat
    def init_heart_beat(self):
        self.register_to_controller()
        self.heart_beat_thread = threading.Thread(
            target=fastchat.serve.model_worker.heart_beat_worker, args=(self,), daemon=True,
        )
        self.heart_beat_thread.start()

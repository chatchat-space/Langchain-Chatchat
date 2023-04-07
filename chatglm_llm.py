from langchain.llms.base import LLM
from typing import Optional, List
from langchain.llms.utils import enforce_stop_tokens
from transformers import AutoTokenizer, AutoModel
import torch

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


tokenizer = AutoTokenizer.from_pretrained(
    "THUDM/chatglm-6b",
    trust_remote_code=True
)
model = (
    AutoModel.from_pretrained(
        "THUDM/chatglm-6b",
        trust_remote_code=True)
    .half()
    .cuda()
)


class ChatGLM(LLM):
    max_token: int = 10000
    temperature: float = 0.1
    top_p = 0.9
    history = []

    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    def _call(self,
              prompt: str,
              stop: Optional[List[str]] = None) -> str:
        response, updated_history = model.chat(
            tokenizer,
            prompt,
            history=self.history,
            max_length=self.max_token,
            temperature=self.temperature,
        )
        print("history: ", self.history)
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = updated_history
        return response

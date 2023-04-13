from langchain.llms.base import LLM
from typing import Optional, List
from langchain.llms.utils import enforce_stop_tokens
from transformers import AutoTokenizer, AutoModel
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
DEVICE_ID = "0" if torch.cuda.is_available() else None
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


class ChatGLM(LLM):
    max_token: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    history = []
    tokenizer: object = None
    model: object = None
    history_len: int = 10

    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    def _call(self,
              prompt: str,
              stop: Optional[List[str]] = None) -> str:
        response, _ = self.model.chat(
            self.tokenizer,
            prompt,
            history=self.history[-self.history_len:] if self.history_len>0 else [],
            max_length=self.max_token,
            temperature=self.temperature,
        )
        torch_gc()
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = self.history+[[None, response]]
        return response

    def load_model(self, model_name_or_path: str = "THUDM/chatglm-6b"):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            trust_remote_code=True
        )
        if torch.cuda.is_available():
            self.model = (
                AutoModel.from_pretrained(
                    model_name_or_path,
                    trust_remote_code=True)
                .half()
                .cuda()
            )
        elif torch.backends.mps.is_available():
            self.model = (
                AutoModel.from_pretrained(
                    model_name_or_path,
                    trust_remote_code=True)
                .float()
                .to('mps')
            )
        else:
            self.model = (
                AutoModel.from_pretrained(
                    model_name_or_path,
                    trust_remote_code=True)
                .float()
            )
        self.model = self.model.eval()

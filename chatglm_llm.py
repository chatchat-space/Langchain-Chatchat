import sys
import itertools
import time
import threading
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


class ChatGLM(LLM):
    max_token: int = 10000
    temperature: float = 0.1
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
            history=self.history[-self.history_len:],
            max_length=self.max_token,
            temperature=self.temperature,
        )
        torch_gc()
        if stop is not None:
            response = enforce_stop_tokens(response, stop)
        self.history = self.history+[[None, response]]
        return response

    def load_model(self,
                   model_name_or_path: str = "THUDM/chatglm-6b",
                   revision: str = "main"):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            revision=revision,
            trust_remote_code=True
        )

        # Set up the rotating progress indicator
        progress_indicator = itertools.cycle(['|', '/', '-', '\\'])

        def display_progress_indicator():
            while not model_loaded:
                sys.stdout.write(next(progress_indicator))
                sys.stdout.flush()
                sys.stdout.write('\b')
                time.sleep(0.1)

        # Create a separate thread for the rotating progress indicator
        model_loaded = False
        progress_thread = threading.Thread(target=display_progress_indicator, daemon=True)
        progress_thread.start()

        # Load the model
        self.model = (
            AutoModel.from_pretrained(
                model_name_or_path,
                revision=revision,
                trust_remote_code=True)
            .half()
            .cuda()
        )

        # Stop the progress indicator thread
        model_loaded = True
        progress_thread.join()

import json
from langchain.llms.base import LLM
from typing import Optional, List
from langchain.llms.utils import enforce_stop_tokens
from transformers import AutoTokenizer, AutoModel, AutoConfig
import torch
from configs.model_config import LLM_DEVICE

DEVICE = LLM_DEVICE
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

    def load_model(self,
                   model_name_or_path: str = "THUDM/chatglm-6b",
                   llm_device=LLM_DEVICE,
                   use_ptuning_v2=False):
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            trust_remote_code=True
        )

        model_config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)

        if use_ptuning_v2:
            try:
                prefix_encoder_file = open('ptuning-v2/config.json', 'r')
                prefix_encoder_config = json.loads(prefix_encoder_file.read())
                prefix_encoder_file.close()
                model_config.pre_seq_len = prefix_encoder_config['pre_seq_len']
                model_config.prefix_projection = prefix_encoder_config['prefix_projection']
            except Exception:
                print("加载PrefixEncoder config.json失败")

        if torch.cuda.is_available() and llm_device.lower().startswith("cuda"):
            self.model = (
                AutoModel.from_pretrained(
                    model_name_or_path,
                    config=model_config,
                    trust_remote_code=True)
                .half()
                .cuda()
            )
        else:
            self.model = (
                AutoModel.from_pretrained(
                    model_name_or_path,
                    config=model_config,
                    trust_remote_code=True)
                .float()
                .to(llm_device)
            )

        if use_ptuning_v2:
            try:
                prefix_state_dict = torch.load('ptuning-v2/pytorch_model.bin')
                new_prefix_state_dict = {}
                for k, v in prefix_state_dict.items():
                    if k.startswith("transformer.prefix_encoder."):
                        new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
                self.model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
                self.model.transformer.prefix_encoder.float()
            except Exception:
                print("加载PrefixEncoder模型参数失败")

        self.model = self.model.eval()

import json
from langchain.llms.base import LLM
from typing import List, Dict, Optional
from transformers import AutoTokenizer, AutoModel, AutoConfig
import torch
from configs.model_config import *
from utils import torch_gc

DEVICE_ = LLM_DEVICE
DEVICE_ID = "0" if torch.cuda.is_available() else None
DEVICE = f"{DEVICE_}:{DEVICE_ID}" if DEVICE_ID else DEVICE_


def auto_configure_device_map(num_gpus: int, use_lora: bool) -> Dict[str, int]:
    # transformer.word_embeddings 占用1层
    # transformer.final_layernorm 和 lm_head 占用1层
    # transformer.layers 占用 28 层
    # 总共30层分配到num_gpus张卡上
    num_trans_layers = 28
    per_gpu_layers = 30 / num_gpus

    # bugfix: PEFT加载lora模型出现的层命名不同
    if LLM_LORA_PATH and use_lora:
        layer_prefix = 'base_model.model.transformer'
    else:
        layer_prefix = 'transformer'

    # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
    # windows下 model.device 会被设置成 transformer.word_embeddings.device
    # linux下 model.device 会被设置成 lm_head.device
    # 在调用chat或者stream_chat时,input_ids会被放到model.device上
    # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
    # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
    device_map = {f'{layer_prefix}.word_embeddings': 0,
                  f'{layer_prefix}.final_layernorm': 0, 'lm_head': 0,
                  f'base_model.model.lm_head': 0, }

    used = 2
    gpu_target = 0
    for i in range(num_trans_layers):
        if used >= per_gpu_layers:
            gpu_target += 1
            used = 0
        assert gpu_target < num_gpus
        device_map[f'{layer_prefix}.layers.{i}'] = gpu_target
        used += 1

    return device_map


class ChatGLM(LLM):
    max_token: int = 10000
    temperature: float = 0.8
    top_p = 0.9
    # history = []
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
              history: List[List[str]] = [],
              streaming: bool = STREAMING):  # -> Tuple[str, List[List[str]]]:
        if streaming:
            for inum, (stream_resp, _) in enumerate(self.model.stream_chat(
                    self.tokenizer,
                    prompt,
                    history=history[-self.history_len:-1] if self.history_len > 0 else [],
                    max_length=self.max_token,
                    temperature=self.temperature,
                    top_p=self.top_p,
            )):
                torch_gc()
                if inum == 0:
                    history += [[prompt, stream_resp]]
                else:
                    history[-1] = [prompt, stream_resp]
                yield stream_resp, history
                torch_gc()
        else:
            response, _ = self.model.chat(
                self.tokenizer,
                prompt,
                history=history[-self.history_len:] if self.history_len > 0 else [],
                max_length=self.max_token,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            torch_gc()
            history += [[prompt, response]]
            yield response, history
            torch_gc()

    # def chat(self,
    #          prompt: str) -> str:
    #     response, _ = self.model.chat(
    #         self.tokenizer,
    #         prompt,
    #         history=self.history[-self.history_len:] if self.history_len > 0 else [],
    #         max_length=self.max_token,
    #         temperature=self.temperature,
    #     )
    #     torch_gc()
    #     self.history = self.history + [[None, response]]
    #     return response

    def load_model(self,
                   model_name_or_path: str = "THUDM/chatglm-6b",
                   llm_device=LLM_DEVICE,
                   use_ptuning_v2=False,
                   use_lora=False,
                   device_map: Optional[Dict[str, int]] = None,
                   **kwargs):
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
            except Exception as e:
                logger.error(f"加载PrefixEncoder config.json失败: {e}")
        self.model = AutoModel.from_pretrained(model_name_or_path, config=model_config, trust_remote_code=True,
                                               **kwargs)
        if LLM_LORA_PATH and use_lora:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, LLM_LORA_PATH)

        if torch.cuda.is_available() and llm_device.lower().startswith("cuda"):
            # 根据当前设备GPU数量决定是否进行多卡部署
            num_gpus = torch.cuda.device_count()
            if num_gpus < 2 and device_map is None:
                self.model = self.model.half().cuda()
            else:
                from accelerate import dispatch_model

                # model = AutoModel.from_pretrained(model_name_or_path, trust_remote_code=True,
                #         config=model_config, **kwargs)
                if LLM_LORA_PATH and use_lora:
                    from peft import PeftModel
                    model = PeftModel.from_pretrained(self.model, LLM_LORA_PATH)
                # 可传入device_map自定义每张卡的部署情况
                if device_map is None:
                    device_map = auto_configure_device_map(num_gpus, use_lora)

                self.model = dispatch_model(self.model.half(), device_map=device_map)
        else:
            self.model = self.model.float().to(llm_device)

        if use_ptuning_v2:
            try:
                prefix_state_dict = torch.load('ptuning-v2/pytorch_model.bin')
                new_prefix_state_dict = {}
                for k, v in prefix_state_dict.items():
                    if k.startswith("transformer.prefix_encoder."):
                        new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
                self.model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
                self.model.transformer.prefix_encoder.float()
            except Exception as e:
                logger.error(f"加载PrefixEncoder模型参数失败:{e}")

        self.model = self.model.eval()


if __name__ == "__main__":
    llm = ChatGLM()
    llm.load_model(model_name_or_path=llm_model_dict[LLM_MODEL],
                   llm_device=LLM_DEVICE, )
    last_print_len = 0
    for resp, history in llm._call("你好", streaming=True):
        logger.info(resp[last_print_len:], end="", flush=True)
        last_print_len = len(resp)
    for resp, history in llm._call("你好", streaming=False):
        logger.info(resp)
    pass

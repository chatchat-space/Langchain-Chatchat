import gc
import json
import os
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union
import torch
import transformers
from transformers import (AutoConfig, AutoModel, AutoModelForCausalLM,
                          AutoTokenizer, LlamaTokenizer)
from configs.model_config import LLM_DEVICE


class LoaderCheckPoint:
    """
    加载自定义 model CheckPoint
    """
    # remote in the model on loader checkpoint
    no_remote_model: bool = False
    # 模型名称
    model_name: str = None
    tokenizer: object = None
    # 模型全路径
    model_path: str = None
    model: object = None
    model_config: object = None
    lora_names: set = []
    model_dir: str = None
    lora_dir: str = None
    ptuning_dir: str = None
    use_ptuning_v2: bool = False
    # 如果开启了8bit量化加载,项目无法启动，参考此位置，选择合适的cuda版本，https://github.com/TimDettmers/bitsandbytes/issues/156
    load_in_8bit: bool = False
    is_llamacpp: bool = False
    bf16: bool = False
    params: object = None
    # 自定义设备网络
    device_map: Optional[Dict[str, int]] = None
    # 默认 cuda ，如果不支持cuda使用多卡， 如果不支持多卡 使用cpu
    llm_device = LLM_DEVICE

    def __init__(self, params: dict = None):
        """
        模型初始化
        :param params:
        """
        self.model_path = None
        self.model = None
        self.tokenizer = None
        self.params = params or {}
        self.no_remote_model = params.get('no_remote_model', False)
        self.model_name = params.get('model', '')
        self.lora = params.get('lora', '')
        self.use_ptuning_v2 = params.get('use_ptuning_v2', False)
        self.model_dir = params.get('model_dir', '')
        self.lora_dir = params.get('lora_dir', '')
        self.ptuning_dir = params.get('ptuning_dir', 'ptuning-v2')
        self.load_in_8bit = params.get('load_in_8bit', False)
        self.bf16 = params.get('bf16', False)

    def _load_model_config(self, model_name):
        checkpoint = Path(f'{self.model_dir}/{model_name}')

        if self.model_path:
            checkpoint = Path(f'{self.model_path}')
        else:
            if not self.no_remote_model:
                checkpoint = model_name

        model_config = AutoConfig.from_pretrained(checkpoint, trust_remote_code=True)

        return model_config

    def _load_model(self, model_name):
        """
        加载自定义位置的model
        :param model_name:
        :return:
        """
        print(f"Loading {model_name}...")
        t0 = time.time()

        checkpoint = Path(f'{self.model_dir}/{model_name}')

        self.is_llamacpp = len(list(checkpoint.glob('ggml*.bin'))) > 0

        if self.model_path:
            checkpoint = Path(f'{self.model_path}')
        else:
            if not self.no_remote_model:
                checkpoint = model_name

        if 'chatglm' in model_name.lower():
            LoaderClass = AutoModel
        else:
            LoaderClass = AutoModelForCausalLM

        # Load the model in simple 16-bit mode by default
        if not any([self.llm_device.lower() == "cpu",
                    self.load_in_8bit, self.is_llamacpp]):

            if torch.cuda.is_available() and self.llm_device.lower().startswith("cuda"):
                # 根据当前设备GPU数量决定是否进行多卡部署
                num_gpus = torch.cuda.device_count()
                if num_gpus < 2 and self.device_map is None:
                    model = (
                        LoaderClass.from_pretrained(checkpoint,
                                                    config=self.model_config,
                                                    torch_dtype=torch.bfloat16 if self.bf16 else torch.float16,
                                                    trust_remote_code=True)
                        .half()
                        .cuda()
                    )
                else:
                    from accelerate import dispatch_model

                    model = LoaderClass.from_pretrained(checkpoint,
                                                        config=self.model_config,
                                                        torch_dtype=torch.bfloat16 if self.bf16 else torch.float16,
                                                        trust_remote_code=True).half()
                    # 可传入device_map自定义每张卡的部署情况
                    if self.device_map is None:
                        if 'chatglm' in model_name.lower():
                            self.device_map = self.chatglm_auto_configure_device_map(num_gpus)
                        elif 'moss' in model_name.lower():
                            self.device_map = self.moss_auto_configure_device_map(num_gpus, model_name)
                        else:
                            self.device_map = self.chatglm_auto_configure_device_map(num_gpus)

                    model = dispatch_model(model, device_map=self.device_map)
            else:
                model = (
                    LoaderClass.from_pretrained(
                        checkpoint,
                        config=self.model_config,
                        trust_remote_code=True)
                    .float()
                    .to(self.llm_device)
                )

        elif self.is_llamacpp:

            try:
                from models.extensions.llamacpp_model_alternative import LlamaCppModel

            except ImportError as exc:
                raise ValueError(
                    "Could not import depend python package "
                    "Please install it with `pip install llama-cpp-python`."
                ) from exc

            model_file = list(checkpoint.glob('ggml*.bin'))[0]
            print(f"llama.cpp weights detected: {model_file}\n")

            model, tokenizer = LlamaCppModel.from_pretrained(model_file)
            return model, tokenizer

        elif self.load_in_8bit:
            try:
                from accelerate import init_empty_weights
                from accelerate.utils import get_balanced_memory, infer_auto_device_map
                from transformers import BitsAndBytesConfig

            except ImportError as exc:
                raise ValueError(
                    "Could not import depend python package "
                    "Please install it with `pip install transformers` "
                    "`pip install bitsandbytes``pip install accelerate`."
                ) from exc

            params = {"low_cpu_mem_usage": True}

            if not self.llm_device.lower().startswith("cuda"):
                raise SystemError("8bit 模型需要 CUDA 支持，或者改用量化后模型！")
            else:
                params["device_map"] = 'auto'
                params["trust_remote_code"] = True
                params['quantization_config'] = BitsAndBytesConfig(load_in_8bit=True,
                                                                   llm_int8_enable_fp32_cpu_offload=False)

            with init_empty_weights():
                model = LoaderClass.from_config(self.model_config,trust_remote_code = True)
            model.tie_weights()
            if self.device_map is not None:
                params['device_map'] = self.device_map
            else:
                params['device_map'] = infer_auto_device_map(
                    model,
                    dtype=torch.int8,
                    no_split_module_classes=model._no_split_modules
                )
            try:

                model = LoaderClass.from_pretrained(checkpoint, **params)
            except ImportError as exc:
                raise ValueError(
                    "如果开启了8bit量化加载,项目无法启动，参考此位置，选择合适的cuda版本，https://github.com/TimDettmers/bitsandbytes/issues/156"
                ) from exc
        # Custom
        else:

            print(
                "Warning: self.llm_device is False.\nThis means that no use GPU  bring to be load CPU mode\n")
            params = {"low_cpu_mem_usage": True, "torch_dtype": torch.float32, "trust_remote_code": True}
            model = LoaderClass.from_pretrained(checkpoint, **params).to(self.llm_device, dtype=float)

        # Loading the tokenizer
        if type(model) is transformers.LlamaForCausalLM:
            tokenizer = LlamaTokenizer.from_pretrained(checkpoint, clean_up_tokenization_spaces=True)
            # Leaving this here until the LLaMA tokenizer gets figured out.
            # For some people this fixes things, for others it causes an error.
            try:
                tokenizer.eos_token_id = 2
                tokenizer.bos_token_id = 1
                tokenizer.pad_token_id = 0
            except Exception as e:
                print(e)
                pass
        else:
            tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)

        print(f"Loaded the model in {(time.time() - t0):.2f} seconds.")
        return model, tokenizer

    def chatglm_auto_configure_device_map(self, num_gpus: int) -> Dict[str, int]:
        # transformer.word_embeddings 占用1层
        # transformer.final_layernorm 和 lm_head 占用1层
        # transformer.layers 占用 28 层
        # 总共30层分配到num_gpus张卡上
        num_trans_layers = 28
        per_gpu_layers = 30 / num_gpus

        # bugfix: PEFT加载lora模型出现的层命名不同
        if self.lora:
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

    def moss_auto_configure_device_map(self, num_gpus: int, model_name) -> Dict[str, int]:
        try:

            from accelerate import init_empty_weights
            from accelerate.utils import get_balanced_memory, infer_auto_device_map
            from transformers.dynamic_module_utils import get_class_from_dynamic_module
            from transformers.modeling_utils import no_init_weights
            from transformers.utils import ContextManagers
        except ImportError as exc:
            raise ValueError(
                "Could not import depend python package "
                "Please install it with `pip install transformers` "
                "`pip install bitsandbytes``pip install accelerate`."
            ) from exc

        checkpoint = Path(f'{self.model_dir}/{model_name}')

        if self.model_path:
            checkpoint = Path(f'{self.model_path}')
        else:
            if not self.no_remote_model:
                checkpoint = model_name
        cls = get_class_from_dynamic_module(class_reference="fnlp/moss-moon-003-sft--modeling_moss.MossForCausalLM",
                                            pretrained_model_name_or_path=checkpoint)

        with ContextManagers([no_init_weights(_enable=True), init_empty_weights()]):
            model = cls(self.model_config)
            max_memory = get_balanced_memory(model, dtype=torch.int8 if self.load_in_8bit else None,
                                             low_zero=False, no_split_module_classes=model._no_split_modules)
            device_map = infer_auto_device_map(
                model, dtype=torch.float16 if not self.load_in_8bit else torch.int8, max_memory=max_memory,
                no_split_module_classes=model._no_split_modules)
            device_map["transformer.wte"] = 0
            device_map["transformer.drop"] = 0
            device_map["transformer.ln_f"] = 0
            device_map["lm_head"] = 0
            return device_map

    def _add_lora_to_model(self, lora_names):

        try:

            from peft import PeftModel

        except ImportError as exc:
            raise ValueError(
                "Could not import depend python package. "
                "Please install it with `pip install peft``pip install accelerate`."
            ) from exc
        # 目前加载的lora
        prior_set = set(self.lora_names)
        # 需要加载的
        added_set = set(lora_names) - prior_set
        # 删除的lora
        removed_set = prior_set - set(lora_names)
        self.lora_names = list(lora_names)

        # Nothing to do = skip.
        if len(added_set) == 0 and len(removed_set) == 0:
            return

        # Only adding, and already peft? Do it the easy way.
        if len(removed_set) == 0 and len(prior_set) > 0:
            print(f"Adding the LoRA(s) named {added_set} to the model...")
            for lora in added_set:
                self.model.load_adapter(Path(f"{self.lora_dir}/{lora}"), lora)
            return

        # If removing anything, disable all and re-add.
        if len(removed_set) > 0:
            self.model.disable_adapter()

        if len(lora_names) > 0:
            print("Applying the following LoRAs to {}: {}".format(self.model_name, ', '.join(lora_names)))
            params = {}
            if self.llm_device.lower() != "cpu":
                params['dtype'] = self.model.dtype
                if hasattr(self.model, "hf_device_map"):
                    params['device_map'] = {"base_model.model." + k: v for k, v in self.model.hf_device_map.items()}
                elif self.load_in_8bit:
                    params['device_map'] = {'': 0}
            self.model.resize_token_embeddings(len(self.tokenizer))

            self.model = PeftModel.from_pretrained(self.model, Path(f"{self.lora_dir}/{lora_names[0]}"), **params)

            for lora in lora_names[1:]:
                self.model.load_adapter(Path(f"{self.lora_dir}/{lora}"), lora)

            if not self.load_in_8bit and self.llm_device.lower() != "cpu":

                if not hasattr(self.model, "hf_device_map"):
                    if torch.has_mps:
                        device = torch.device('mps')
                        self.model = self.model.to(device)
                    else:
                        self.model = self.model.cuda()

    def clear_torch_cache(self):
        gc.collect()
        if self.llm_device.lower() != "cpu":
            if torch.has_mps:
                try:
                    from torch.mps import empty_cache
                    empty_cache()
                except Exception as e:
                    print(e)
                    print(
                        "如果您使用的是 macOS 建议将 pytorch 版本升级至 2.0.0 或更高版本，以支持及时清理 torch 产生的内存占用。")
            elif torch.has_cuda:
                device_id = "0" if torch.cuda.is_available() else None
                CUDA_DEVICE = f"{self.llm_device}:{device_id}" if device_id else self.llm_device
                with torch.cuda.device(CUDA_DEVICE):
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            else:
                print("未检测到 cuda 或 mps，暂不支持清理显存")

    def unload_model(self):
        del self.model
        del self.tokenizer
        self.model = self.tokenizer = None
        self.clear_torch_cache()

    def set_model_path(self, model_path):
        self.model_path = model_path

    def reload_model(self):
        self.unload_model()
        self.model_config = self._load_model_config(self.model_name)

        if self.use_ptuning_v2:
            try:
                prefix_encoder_file = open(Path(f'{self.ptuning_dir}/config.json'), 'r')
                prefix_encoder_config = json.loads(prefix_encoder_file.read())
                prefix_encoder_file.close()
                self.model_config.pre_seq_len = prefix_encoder_config['pre_seq_len']
                self.model_config.prefix_projection = prefix_encoder_config['prefix_projection']
            except Exception as e:
                print("加载PrefixEncoder config.json失败")

        self.model, self.tokenizer = self._load_model(self.model_name)

        if self.lora:
            self._add_lora_to_model([self.lora])

        if self.use_ptuning_v2:
            try:
                prefix_state_dict = torch.load(Path(f'{self.ptuning_dir}/pytorch_model.bin'))
                new_prefix_state_dict = {}
                for k, v in prefix_state_dict.items():
                    if k.startswith("transformer.prefix_encoder."):
                        new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
                self.model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
                self.model.transformer.prefix_encoder.float()
            except Exception as e:
                print("加载PrefixEncoder模型参数失败")

        self.model = self.model.eval()

# chatchat加载ptuning指南

P-tuning虽然是一种peft方法，但并不能于huggingface的peft python包兼容，而fastchat在多处以字符串匹配的方式进行硬编码加载模型，因此导致fastchat和chatchat不能兼容p-tuning，经langchain-chatchat开发组多次尝试，给出如下指南进行p-tuning加载。

# 1. peft文件夹修改

1. 将config.json文件修改为adapter_config.json;
2. 保证文件夹包含pytorch_model.bin文件；
3. 修改文件夹名称，保证文件夹包含'peft'一词；
4. 在adapter_config.json文件中增加如下字段：

   ```json
       "base_model_name_or_path": "/root/model/chatglm2-6b/"
       "task_type": "CAUSAL_LM",
       "peft_type": "PREFIX_TUNING",
       "inference_mode": true,
       "revision": "main",
       "num_virtual_tokens": 16
   ```

   **其中,"base_model_name_or_path"为基础模型的存在位置**；
5. 将文件夹移入项目文件夹中，如Langchain-Chatchat项目文件夹目录下；

# 2. fastchat包代码修改

## 2.1 fastchat.model.model_adapter文件修改

1. 将fastchat.model.model_adapter.py文件的load_model函数修改为：

   ```python
   def load_model(
       model_path: str,
       device: str = "cuda",
       num_gpus: int = 1,
       max_gpu_memory: Optional[str] = None,
       dtype: Optional[torch.dtype] = None,
       load_8bit: bool = False,
       cpu_offloading: bool = False,
       gptq_config: Optional[GptqConfig] = None,
       awq_config: Optional[AWQConfig] = None,
       revision: str = "main",
       debug: bool = False,
       load_kwargs = {}
   ):
       """Load a model from Hugging Face."""
       # get model adapter
       adapter = get_model_adapter(model_path)
       kwargs = load_kwargs
       # Handle device mapping
       cpu_offloading = raise_warning_for_incompatible_cpu_offloading_configuration(
           device, load_8bit, cpu_offloading
       )
       if device == "cpu":
           kwargs["torch_dtype"]= torch.float32
           if CPU_ISA in ["avx512_bf16", "amx"]:
               try:
                   import intel_extension_for_pytorch as ipex

                   kwargs ["torch_dtype"]= torch.bfloat16
               except ImportError:
                   warnings.warn(
                       "Intel Extension for PyTorch is not installed, it can be installed to accelerate cpu inference"
                   )
       elif device == "cuda":
           kwargs["torch_dtype"] = torch.float16
           if num_gpus != 1:
               kwargs["device_map"] = "auto"
               if max_gpu_memory is None:
                   kwargs[
                       "device_map"
                   ] = "sequential"  # This is important for not the same VRAM sizes
                   available_gpu_memory = get_gpu_memory(num_gpus)
                   kwargs["max_memory"] = {
                       i: str(int(available_gpu_memory[i] * 0.85)) + "GiB"
                       for i in range(num_gpus)
                   }
               else:
                   kwargs["max_memory"] = {i: max_gpu_memory for i in range(num_gpus)}
       elif device == "mps":
           kwargs["torch_dtype"] = torch.float16
           # Avoid bugs in mps backend by not using in-place operations.
           replace_llama_attn_with_non_inplace_operations()
       elif device == "xpu":
           kwargs["torch_dtype"] = torch.bfloat16
           # Try to load ipex, while it looks unused, it links into torch for xpu support
           try:
               import intel_extension_for_pytorch as ipex
           except ImportError:
               warnings.warn(
                   "Intel Extension for PyTorch is not installed, but is required for xpu inference."
               )
       elif device == "npu":
           kwargs["torch_dtype"]= torch.float16
           # Try to load ipex, while it looks unused, it links into torch for xpu support
           try:
               import torch_npu
           except ImportError:
               warnings.warn("Ascend Extension for PyTorch is not installed.")
       else:
           raise ValueError(f"Invalid device: {device}")

       if cpu_offloading:
           # raises an error on incompatible platforms
           from transformers import BitsAndBytesConfig

           if "max_memory" in kwargs:
               kwargs["max_memory"]["cpu"] = (
                   str(math.floor(psutil.virtual_memory().available / 2**20)) + "Mib"
               )
           kwargs["quantization_config"] = BitsAndBytesConfig(
               load_in_8bit_fp32_cpu_offload=cpu_offloading
           )
           kwargs["load_in_8bit"] = load_8bit
       elif load_8bit:
           if num_gpus != 1:
               warnings.warn(
                   "8-bit quantization is not supported for multi-gpu inference."
               )
           else:
               model, tokenizer = adapter.load_compress_model(
                   model_path=model_path,
                   device=device,
                   torch_dtype=kwargs["torch_dtype"],
                   revision=revision,
               )
               if debug:
                   print(model)
               return model, tokenizer
       elif awq_config and awq_config.wbits < 16:
           assert (
               awq_config.wbits == 4
           ), "Currently we only support 4-bit inference for AWQ."
           model, tokenizer = load_awq_quantized(model_path, awq_config, device)
           if num_gpus != 1:
               device_map = accelerate.infer_auto_device_map(
                   model,
                   max_memory=kwargs["max_memory"],
                   no_split_module_classes=[
                       "OPTDecoderLayer",
                       "LlamaDecoderLayer",
                       "BloomBlock",
                       "MPTBlock",
                       "DecoderLayer",
                   ],
               )
               model = accelerate.dispatch_model(
                   model, device_map=device_map, offload_buffers=True
               )
           else:
               model.to(device)
           return model, tokenizer
       elif gptq_config and gptq_config.wbits < 16:
           model, tokenizer = load_gptq_quantized(model_path, gptq_config)
           if num_gpus != 1:
               device_map = accelerate.infer_auto_device_map(
                   model,
                   max_memory=kwargs["max_memory"],
                   no_split_module_classes=["LlamaDecoderLayer"],
               )
               model = accelerate.dispatch_model(
                   model, device_map=device_map, offload_buffers=True
               )
           else:
               model.to(device)
           return model, tokenizer
       kwargs["revision"] = revision

       if dtype is not None:  # Overwrite dtype if it is provided in the arguments.
           kwargs["torch_dtype"] = dtype

       # Load model
       model, tokenizer = adapter.load_model(model_path, kwargs)

       if (
           device == "cpu"
           and kwargs["torch_dtype"] is torch.bfloat16
           and CPU_ISA is not None
       ):
           model = ipex.optimize(model, dtype=kwargs["torch_dtype"])

       if (device == "cuda" and num_gpus == 1 and not cpu_offloading) or device in (
           "mps",
           "xpu",
           "npu",
       ):
           model.to(device)

       if device == "xpu":
           model = torch.xpu.optimize(model, dtype=kwargs["torch_dtype"], inplace=True)

       if debug:
           print(model)

       return model, tokenizer
   ```
2. 将fastchat.model.model_adapter.py的函数修改为：

   ```python
   def get_generate_stream_function(model: torch.nn.Module, model_path: str):
       """Get the generate_stream function for inference."""
       from fastchat.serve.inference import generate_stream

       model_type = str(type(model)).lower()

       is_chatglm = "chatglm" in model_type 
       is_falcon = "rwforcausallm" in model_type
       is_codet5p = "codet5p" in model_type 
       is_peft = "peft" in model_type

       if is_chatglm:
           return generate_stream_chatglm
       elif is_falcon:
           return generate_stream_falcon
       elif is_codet5p:
           return generate_stream_codet5p
       elif peft_share_base_weights and is_peft:
           # Return a curried stream function that loads the right adapter
           # according to the model_name available in this context.  This ensures
           # the right weights are available.
           @torch.inference_mode()
           def generate_stream_peft(
               model,
               tokenizer,
               params: Dict,
               device: str,
               context_len: int,
               stream_interval: int = 2,
               judge_sent_end: bool = False,
           ):

               model.set_adapter(model_path)
               if "chatglm" in str(type(model.base_model)).lower():
                   model.disable_adapter()
                   prefix_state_dict = torch.load(os.path.join(model_path, "pytorch_model.bin"))
                   new_prefix_state_dict = {}

                   for k, v in prefix_state_dict.items():
                       if k.startswith("transformer.prefix_encoder."):
                           new_prefix_state_dict[k[len("transformer.prefix_encoder."):]] = v
                       elif k.startswith("transformer.prompt_encoder."):
                           new_prefix_state_dict[k[len("transformer.prompt_encoder."):]] = v
                   model.transformer.prefix_encoder.load_state_dict(new_prefix_state_dict)
                   for x in generate_stream_chatglm(
                       model,
                       tokenizer,
                       params,
                       device,
                       context_len,
                       stream_interval,
                       judge_sent_end,
                   ):
                       yield x
               elif "rwforcausallm" in str(type(model.base_model)).lower():

                   for x in generate_stream_falcon(
                       model,
                       tokenizer,
                       params,
                       device,
                       context_len,
                       stream_interval,
                       judge_sent_end,
                   ):
                       yield x   
               elif "codet5p" in str(type(model.base_model)).lower():

                   for x in generate_stream_codet5p(
                       model,
                       tokenizer,
                       params,
                       device,
                       context_len,
                       stream_interval,
                       judge_sent_end,
                   ):
                       yield x   
               else:

                   for x in generate_stream(
                       model,
                       tokenizer,
                       params,
                       device,
                       context_len,
                       stream_interval,
                       judge_sent_end,
                   ):
                       yield x

           return generate_stream_peft
       else:
           return generate_stream
   ```
3. 将fastchat.model.model_adapter.py的PeftModelAdapter类的load_model方法修改为：

   ```python
       def load_model(self, model_path: str, from_pretrained_kwargs: dict):
           """Loads the base model then the (peft) adapter weights"""
           from peft import PeftConfig, PeftModel

           config = PeftConfig.from_pretrained(model_path)
           base_model_path = config.base_model_name_or_path
           if "peft" in base_model_path:
               raise ValueError(
                   f"PeftModelAdapter cannot load a base model with 'peft' in the name: {config.base_model_name_or_path}"
               )

           # Basic proof of concept for loading peft adapters that share the base
           # weights.  This is pretty messy because Peft re-writes the underlying
           # base model and internally stores a map of adapter layers.
           # So, to make this work we:
           #  1. Cache the first peft model loaded for a given base models.
           #  2. Call `load_model` for any follow on Peft models.
           #  3. Make sure we load the adapters by the model_path.  Why? This is
           #  what's accessible during inference time.
           #  4. In get_generate_stream_function, make sure we load the right
           #  adapter before doing inference.  This *should* be safe when calls
           #  are blocked the same semaphore.
           if peft_share_base_weights:
               if base_model_path in peft_model_cache:
                   model, tokenizer = peft_model_cache[base_model_path]
                   # Super important: make sure we use model_path as the
                   # `adapter_name`.
                   model.load_adapter(model_path, adapter_name=model_path)
               else:
                   base_adapter = get_model_adapter(base_model_path)
                   base_model, tokenizer = base_adapter.load_model(
                       base_model_path, from_pretrained_kwargs
                   )
                   # Super important: make sure we use model_path as the
                   # `adapter_name`.
                   from peft import get_peft_model
                   model = get_peft_model(base_model,config,adapter_name=model_path)
                   peft_model_cache[base_model_path] = (model, tokenizer)
               return model, tokenizer

           # In the normal case, load up the base model weights again.
           base_adapter = get_model_adapter(base_model_path)
           base_model, tokenizer = base_adapter.load_model(
               base_model_path, from_pretrained_kwargs
           )
           from peft import get_peft_model
           model = get_peft_model(base_model,config,adapter_name=model_path)
           return model, tokenizer

   ```
4. 将fastchat.model.model_adapter.py的ChatglmAdapter类的load_model方法修改为：

   ```python
       def load_model(self, model_path: str, from_pretrained_kwargs: dict):
           revision = from_pretrained_kwargs.get("revision", "main")
           tokenizer = AutoTokenizer.from_pretrained(
               model_path, trust_remote_code=True, revision=revision
           )
           config = AutoConfig.from_pretrained(model_path, trust_remote_code=True,**from_pretrained_kwargs)
           model = AutoModel.from_pretrained(
               model_path, trust_remote_code=True, config=config
           )
           return model, tokenizer
   ```

## 2.2 fastchat.serve.model_worker文件修改

1. 将fastchat.serve.model_worker文件的ModelWorker的__init__方法修改如下：

   ```python
   class ModelWorker(BaseModelWorker):
       def __init__(
           self,
           controller_addr: str,
           worker_addr: str,
           worker_id: str,
           model_path: str,
           model_names: List[str],
           limit_worker_concurrency: int,
           no_register: bool,
           device: str,
           num_gpus: int,
           max_gpu_memory: str,
           dtype: Optional[torch.dtype] = None,
           load_8bit: bool = False,
           cpu_offloading: bool = False,
           gptq_config: Optional[GptqConfig] = None,
           awq_config: Optional[AWQConfig] = None,
           stream_interval: int = 2,
           conv_template: Optional[str] = None,
           embed_in_truncate: bool = False,
           seed: Optional[int] = None,
           load_kwargs = {}, #修改点
           **kwargs,
       ):
           super().__init__(
               controller_addr,
               worker_addr,
               worker_id,
               model_path,
               model_names,
               limit_worker_concurrency,
               conv_template=conv_template,
           )

           logger.info(f"Loading the model {self.model_names} on worker {worker_id} ...")
           self.model, self.tokenizer = load_model(
               model_path,
               device=device,
               num_gpus=num_gpus,
               max_gpu_memory=max_gpu_memory,
               dtype=dtype,
               load_8bit=load_8bit,
               cpu_offloading=cpu_offloading,
               gptq_config=gptq_config,
               awq_config=awq_config,
               load_kwargs=load_kwargs #修改点
           )
           self.device = device
           if self.tokenizer.pad_token == None:
               self.tokenizer.pad_token = self.tokenizer.eos_token
           self.context_len = get_context_length(self.model.config)
           print("**"*100)
           self.generate_stream_func = get_generate_stream_function(self.model, model_path)
           print(f"self.generate_stream_func{self.generate_stream_func}")
           print("*"*100)
           self.stream_interval = stream_interval
           self.embed_in_truncate = embed_in_truncate
           self.seed = seed

           if not no_register:
               self.init_heart_beat()
   ```
2. 在fastchat.serve.model_worker文件的create_model_worker增加如下args参数：

   ```python
   parser.add_argument("--load_kwargs",type=dict,default={})
   ```

    并将如下语句：

```python
    worker = ModelWorker(
        args.controller_address,
        args.worker_address,
        worker_id,
        args.model_path,
        args.model_names,
        args.limit_worker_concurrency,
        no_register=args.no_register,
        device=args.device,
        num_gpus=args.num_gpus,
        max_gpu_memory=args.max_gpu_memory,
        dtype=str_to_torch_dtype(args.dtype),
        load_8bit=args.load_8bit,
        cpu_offloading=args.cpu_offloading,
        gptq_config=gptq_config,
        awq_config=awq_config,
        stream_interval=args.stream_interval,
        conv_template=args.conv_template,
        embed_in_truncate=args.embed_in_truncate,
        seed=args.seed,
    )
```

修改为：

```python
    worker = ModelWorker(
        args.controller_address,
        args.worker_address,
        worker_id,
        args.model_path,
        args.model_names,
        args.limit_worker_concurrency,
        no_register=args.no_register,
        device=args.device,
        num_gpus=args.num_gpus,
        max_gpu_memory=args.max_gpu_memory,
        dtype=str_to_torch_dtype(args.dtype),
        load_8bit=args.load_8bit,
        cpu_offloading=args.cpu_offloading,
        gptq_config=gptq_config,
        awq_config=awq_config,
        stream_interval=args.stream_interval,
        conv_template=args.conv_template,
        embed_in_truncate=args.embed_in_truncate,
        seed=args.seed,
        load_kwargs=args.load_kwargs
    )
```

至此，我们完成了fastchat加载ptuning的所有修改，在调用fastchat加载p-tuning时，可以通过加入 `PEFT_SHARE_BASE_WEIGHTS=true`，并以字典的形式添加--load_kwargs参数为训练ptuning时的pre_seq_len值即可，例如将2.2.2步骤中的 `parser.add_argument("--load_kwargs",type=dict,default={})`修改为：

`parser.add_argument("--load_kwargs",type=dict,default={"pre_seq_len":16})`

# 3 langchain-chatchat代码修改：

1. 在configs/serve_config.py中的FSCHAT_MODEL_WORKERS字典中增加如下字段：

   ```
   "load_kwargs": {"pre_seq_len": 16} #值修改为adapter_config.json中的pre_seq_len值
   ```
2. 将startup.py中的create_model_worker_app修改为：

   ```python
   def create_model_worker_app(log_level: str = "INFO", **kwargs) -> FastAPI:
       """
       kwargs包含的字段如下：
       host:
       port:
       model_names:[`model_name`]
       controller_address:
       worker_address:


       对于online_api:
           online_api:True
           worker_class: `provider`
       对于离线模型：
           model_path: `model_name_or_path`,huggingface的repo-id或本地路径
           device:`LLM_DEVICE`
       """
       import fastchat.constants
       fastchat.constants.LOGDIR = LOG_PATH
       from fastchat.serve.model_worker import worker_id, logger
       import argparse
       logger.setLevel(log_level)

       parser = argparse.ArgumentParser()
       args = parser.parse_args([])

       for k, v in kwargs.items():
           setattr(args, k, v)

       # 在线模型API
       if worker_class := kwargs.get("worker_class"):
           from fastchat.serve.model_worker import app
           worker = worker_class(model_names=args.model_names,
                                 controller_addr=args.controller_address,
                                 worker_addr=args.worker_address)
           sys.modules["fastchat.serve.model_worker"].worker = worker
       # 本地模型
       else:
           from configs.model_config import VLLM_MODEL_DICT
           if kwargs["model_names"][0] in VLLM_MODEL_DICT and args.infer_turbo == "vllm":
               import fastchat.serve.vllm_worker
               from fastchat.serve.vllm_worker import VLLMWorker,app
               from vllm import AsyncLLMEngine
               from vllm.engine.arg_utils import AsyncEngineArgs,EngineArgs
               args.tokenizer = args.model_path # 如果tokenizer与model_path不一致在此处添加
               args.tokenizer_mode = 'auto'
               args.trust_remote_code= True
               args.download_dir= None
               args.load_format = 'auto'
               args.dtype = 'auto'
               args.seed = 0
               args.worker_use_ray = False
               args.pipeline_parallel_size = 1
               args.tensor_parallel_size = 1
               args.block_size = 16
               args.swap_space = 4  # GiB
               args.gpu_memory_utilization = 0.90
               args.max_num_batched_tokens = 2560
               args.max_num_seqs = 256
               args.disable_log_stats = False
               args.conv_template = None
               args.limit_worker_concurrency = 5
               args.no_register = False
               args.num_gpus = 1 # vllm worker的切分是tensor并行，这里填写显卡的数量
               args.engine_use_ray = False
               args.disable_log_requests = False
               if args.model_path:
                   args.model = args.model_path
               if args.num_gpus > 1:
                   args.tensor_parallel_size = args.num_gpus

               for k, v in kwargs.items():
                   setattr(args, k, v)

               engine_args = AsyncEngineArgs.from_cli_args(args)
               engine = AsyncLLMEngine.from_engine_args(engine_args)

               worker = VLLMWorker(
                           controller_addr = args.controller_address,
                           worker_addr = args.worker_address,
                           worker_id = worker_id,
                           model_path = args.model_path,
                           model_names = args.model_names,
                           limit_worker_concurrency = args.limit_worker_concurrency,
                           no_register = args.no_register,
                           llm_engine =  engine,
                           conv_template = args.conv_template,
                           )
               sys.modules["fastchat.serve.vllm_worker"].engine = engine
               sys.modules["fastchat.serve.vllm_worker"].worker = worker

           else:
               from fastchat.serve.model_worker import app, GptqConfig, AWQConfig, ModelWorker
               args.gpus = "0" # GPU的编号,如果有多个GPU，可以设置为"0,1,2,3"
               args.max_gpu_memory = "20GiB"
               args.num_gpus = 1  # model worker的切分是model并行，这里填写显卡的数量

               args.load_8bit = False
               args.cpu_offloading = None
               args.gptq_ckpt = None
               args.gptq_wbits = 16
               args.gptq_groupsize = -1
               args.gptq_act_order = False
               args.awq_ckpt = None
               args.awq_wbits = 16
               args.awq_groupsize = -1
               args.model_names = []
               args.conv_template = None
               args.limit_worker_concurrency = 5
               args.stream_interval = 2
               args.no_register = False
               args.embed_in_truncate = False
               args.load_kwargs = {"pre_seq_len": 16} # 改*************************
               for k, v in kwargs.items():
                   setattr(args, k, v)
               if args.gpus:
                   if args.num_gpus is None:
                       args.num_gpus = len(args.gpus.split(','))
                   if len(args.gpus.split(",")) < args.num_gpus:
                       raise ValueError(
                           f"Larger --num-gpus ({args.num_gpus}) than --gpus {args.gpus}!"
                       )
                   os.environ["CUDA_VISIBLE_DEVICES"] = args.gpus
               gptq_config = GptqConfig(
                   ckpt=args.gptq_ckpt or args.model_path,
                   wbits=args.gptq_wbits,
                   groupsize=args.gptq_groupsize,
                   act_order=args.gptq_act_order,
               )
               awq_config = AWQConfig(
                   ckpt=args.awq_ckpt or args.model_path,
                   wbits=args.awq_wbits,
                   groupsize=args.awq_groupsize,
               )

               worker = ModelWorker(
                   controller_addr=args.controller_address,
                   worker_addr=args.worker_address,
                   worker_id=worker_id,
                   model_path=args.model_path,
                   model_names=args.model_names,
                   limit_worker_concurrency=args.limit_worker_concurrency,
                   no_register=args.no_register,
                   device=args.device,
                   num_gpus=args.num_gpus,
                   max_gpu_memory=args.max_gpu_memory,
                   load_8bit=args.load_8bit,
                   cpu_offloading=args.cpu_offloading,
                   gptq_config=gptq_config,
                   awq_config=awq_config,
                   stream_interval=args.stream_interval,
                   conv_template=args.conv_template,
                   embed_in_truncate=args.embed_in_truncate,
                   load_kwargs=args.load_kwargs #改*************************
               )
               sys.modules["fastchat.serve.model_worker"].args = args
               sys.modules["fastchat.serve.model_worker"].gptq_config = gptq_config

               sys.modules["fastchat.serve.model_worker"].worker = worker

       MakeFastAPIOffline(app)
       app.title = f"FastChat LLM Server ({args.model_names[0]})"
       app._worker = worker
       return app
   ```

至此，我们完成了langchain-chatchat加载p-tuning的全部操作，可以如下方式加载p-tuning：

```shell
PEFT_SHARE_BASE_WEIGHTS=true python startup.py -a

```

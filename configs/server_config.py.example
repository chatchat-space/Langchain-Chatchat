from .model_config import LLM_MODEL, llm_model_dict, LLM_DEVICE
import httpx

# httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
HTTPX_DEFAULT_TIMEOUT = 300.0

# API 是否开启跨域，默认为False，如果需要开启，请设置为True
# is open cross domain
OPEN_CROSS_DOMAIN = False

# 各服务器默认绑定host
DEFAULT_BIND_HOST = "127.0.0.1"

# webui.py server
WEBUI_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 8501,
}

# api.py server
API_SERVER = {
    "host": DEFAULT_BIND_HOST,
    "port": 7861,
}

# fastchat openai_api server
FSCHAT_OPENAI_API = {
    "host": DEFAULT_BIND_HOST,
    "port": 8888,  # model_config.llm_model_dict中模型配置的api_base_url需要与这里一致。
}

# fastchat model_worker server
# 这些模型必须是在model_config.llm_model_dict中正确配置的。
# 在启动startup.py时，可用通过`--model-worker --model-name xxxx`指定模型，不指定则为LLM_MODEL
FSCHAT_MODEL_WORKERS = {
    # 所有模型共用的默认配置，可在模型专项配置或llm_model_dict中进行覆盖。
    "default": {
        "host": DEFAULT_BIND_HOST,
        "port": 20002,
        "device": LLM_DEVICE,

        # 多卡加载需要配置的参数
        # "gpus": None, # 使用的GPU，以str的格式指定，如"0,1"
        # "num_gpus": 1, # 使用GPU的数量
        # "max_gpu_memory": "20GiB", # 每个GPU占用的最大显存

        # 以下为非常用参数，可根据需要配置
        # "load_8bit": False, # 开启8bit量化
        # "cpu_offloading": None,
        # "gptq_ckpt": None,
        # "gptq_wbits": 16,
        # "gptq_groupsize": -1,
        # "gptq_act_order": False,
        # "awq_ckpt": None,
        # "awq_wbits": 16,
        # "awq_groupsize": -1,
        # "model_names": [LLM_MODEL],
        # "conv_template": None,
        # "limit_worker_concurrency": 5,
        # "stream_interval": 2,
        # "no_register": False,
        # "embed_in_truncate": False,
    },
    "baichuan-7b": { # 使用default中的IP和端口
        "device": "cpu",
    },
    "zhipu-api": { # 请为每个在线API设置不同的端口
        "port": 20003,
    },
    "minimax-api": { # 请为每个在线API设置不同的端口
        "port": 20004,
    },
    "xinghuo-api": { # 请为每个在线API设置不同的端口
        "port": 20005,
    },
    "qianfan-api": {
        "port": 20006,
    },
}

# fastchat multi model worker server
FSCHAT_MULTI_MODEL_WORKERS = {
    # TODO:
}

# fastchat controller server
FSCHAT_CONTROLLER = {
    "host": DEFAULT_BIND_HOST,
    "port": 20001,
    "dispatch_method": "shortest_queue",
}

from .model_config import LLM_MODEL, LLM_DEVICE

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
    LLM_MODEL: {
        "host": DEFAULT_BIND_HOST,
        "port": 20002,
        "device": LLM_DEVICE,
        # todo: 多卡加载需要配置的参数
        "gpus": None, # 使用的GPU，以str的格式指定，如"0,1"
        "num_gpus": 1, # 使用GPU的数量
        # 以下为非常用参数，可根据需要配置
        # "max_gpu_memory": "20GiB", # 每个GPU占用的最大显存
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
    },
}

# fastchat multi model worker server
FSCHAT_MULTI_MODEL_WORKERS = {
    # todo
}

# fastchat controller server
FSCHAT_CONTROLLER = {
    "host": DEFAULT_BIND_HOST,
    "port": 20001,
    "dispatch_method": "shortest_queue",
}


# 以下不要更改
def fschat_controller_address() -> str:
    host = FSCHAT_CONTROLLER["host"]
    port = FSCHAT_CONTROLLER["port"]
    return f"http://{host}:{port}"


def fschat_model_worker_address(model_name: str = LLM_MODEL) -> str:
    if model := FSCHAT_MODEL_WORKERS.get(model_name):
        host = model["host"]
        port = model["port"]
        return f"http://{host}:{port}"


def fschat_openai_api_address() -> str:
    host = FSCHAT_OPENAI_API["host"]
    port = FSCHAT_OPENAI_API["port"]
    return f"http://{host}:{port}"


def api_address() -> str:
    host = API_SERVER["host"]
    port = API_SERVER["port"]
    return f"http://{host}:{port}"


def webui_address() -> str:
    host = WEBUI_SERVER["host"]
    port = WEBUI_SERVER["port"]
    return f"http://{host}:{port}"

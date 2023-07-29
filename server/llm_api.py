from multiprocessing import Process, Queue
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs.model_config import llm_model_dict, LLM_MODEL, LLM_DEVICE, LOG_PATH, logger
import asyncio


host_ip = "0.0.0.0"
controller_port = 20001
model_worker_port = 20002
openai_api_port = 8888
base_url = "http://127.0.0.1:{}"
queue = Queue()


def set_httpx_timeout(timeout=60.0):
    import httpx
    httpx._config.DEFAULT_TIMEOUT_CONFIG.connect = timeout
    httpx._config.DEFAULT_TIMEOUT_CONFIG.read = timeout
    httpx._config.DEFAULT_TIMEOUT_CONFIG.write = timeout


def create_controller_app(
    dispatch_method="shortest_queue",
):
    from fastchat.serve.controller import app, Controller
    from loguru import logger
    logger.add(os.path.join(LOG_PATH, "controller.log"), level="INFO")

    controller = Controller(dispatch_method)
    sys.modules["fastchat.serve.controller"].controller = controller
    sys.modules["fastchat.serve.controller"].logger = logger
    logger.info(f"controller dispatch method: {dispatch_method}")
    return app


def create_model_worker_app(
    model_path=llm_model_dict[LLM_MODEL].get("local_model_path"),
    model_names=[LLM_MODEL],
    device=LLM_DEVICE,
    load_8bit=False,
    gptq_ckpt=None,
    gptq_wbits=16,
    gpus=None,
    num_gpus=1,
    max_gpu_memory=None,
    cpu_offloading=None,
    worker_address=base_url.format(model_worker_port),
    controller_address=base_url.format(controller_port),
    limit_model_concurrency=5,
    stream_interval=2,
    no_register=False,
):
    from fastchat.serve.model_worker import app, GptqConfig, ModelWorker, worker_id
    from fastchat.serve import model_worker
    from loguru import logger
    logger.add(os.path.join(LOG_PATH, "model_worker.log"), level="INFO")

    if gpus and num_gpus is None:
        num_gpus = len(gpus.split(','))
    gptq_config = GptqConfig(
        ckpt=gptq_ckpt or model_path,
        wbits=gptq_wbits,
        groupsize=-1,
        act_order=None,
    )
    worker = ModelWorker(
        controller_address,
        worker_address,
        worker_id,
        no_register,
        model_path,
        model_names,
        device,
        num_gpus,
        max_gpu_memory,
        load_8bit,
        cpu_offloading,
        gptq_config,
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    sys.modules["fastchat.serve.model_worker"].gptq_config = gptq_config
    sys.modules["fastchat.serve.model_worker"].logger = logger
    return app


def create_openai_api_app(
    host=host_ip,
    port=openai_api_port,
    controller_address=base_url.format(controller_port),
    api_keys=[],
):
    from fastchat.serve.openai_api_server import app, CORSMiddleware, app_settings
    from loguru import logger
    logger.add(os.path.join(LOG_PATH, "openai_api.log"), level="INFO")

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app_settings.controller_address = controller_address
    app_settings.api_keys = api_keys
    sys.modules["fastchat.serve.openai_api_server"].logger = logger

    return app


def run_controller(q):
    import uvicorn
    app = create_controller_app()

    @app.on_event("startup")
    async def on_startup():
        set_httpx_timeout()
        q.put(1)

    uvicorn.run(app, host=host_ip, port=controller_port)


def run_model_worker(q):
    import uvicorn
    app = create_model_worker_app()

    @app.on_event("startup")
    async def on_startup():
        set_httpx_timeout()
        while True:
            no = q.get()
            if no != 1:
                q.put(no)
            else:
                break
        q.put(2)

    uvicorn.run(app, host=host_ip, port=model_worker_port)


def run_openai_api(q):
    import uvicorn
    app = create_openai_api_app()

    @app.on_event("startup")
    async def on_startup():
        set_httpx_timeout()
        while True:
            no = q.get()
            if no != 2:
                q.put(no)
            else:
                break
        q.put(3)

    uvicorn.run(app, host=host_ip, port=openai_api_port)


# 1. llm_model_dict精简；

# 2. 不同任务的日志还是分开；

# 3. 在model_config.py里定义args；

# 4. 用logger.removeHandler把它添加的handler删掉，添加我们自己的handler;

# 5. 用watchdog监控第二步的执行情况；

# 6. requirements指定fastchat版本号。

if __name__ == "__main__":
    logger.info(llm_model_dict[LLM_MODEL])
    model_path = llm_model_dict[LLM_MODEL]["local_model_path"]
    model_path = "d:\\chatglm\\models\\chatglm-6b"


    logger.info(f"如需查看 llm_api 日志，请前往 {LOG_PATH}")

    if not model_path:
        logger.error("local_model_path 不能为空")
    else:
        controller_process = Process(
            target=run_controller,
            name=f"controller({os.getpid()})",
            args=(queue,),
            daemon=True,
        )
        controller_process.start()

        model_worker_process = Process(
            target=run_model_worker,
            name=f"model_worker({os.getpid()})",
            args=(queue,),
            daemon=True,
        )
        model_worker_process.start()

        openai_api_process = Process(
            target=run_openai_api,
            name=f"openai_api({os.getpid()})",
            args=(queue,),
            daemon=True,
        )
        openai_api_process.start()

        controller_process.join()
        model_worker_process.join()
        openai_api_process.join()


# 服务启动后接口调用示例：
# import openai
# openai.api_key = "EMPTY" # Not support yet
# openai.api_base = "http://0.0.0.0:8000/v1"

# model = "chatglm2-6b"

# # create a chat completion
# completion = openai.ChatCompletion.create(
#   model=model,
#   messages=[{"role": "user", "content": "Hello! What is your name?"}]
# )
# # print the completion
# print(completion.choices[0].message.content)

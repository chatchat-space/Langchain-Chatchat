from multiprocessing import Process, Queue
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs.model_config import llm_model_dict, LLM_MODEL, LLM_DEVICE, LOG_PATH, logger

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
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.controller import app, Controller

    controller = Controller(dispatch_method)
    sys.modules["fastchat.serve.controller"].controller = controller

    return app


def create_model_worker_app(
        model_path=llm_model_dict[LLM_MODEL].get("local_model_path"),
        model_names=[LLM_MODEL],
        device=LLM_DEVICE,
        load_8bit=False,
        gptq_ckpt=None,
        gptq_wbits=16,
        gptq_groupsize=-1,
        gptq_act_order=None,
        gpus=None,
        num_gpus=1,
        max_gpu_memory="20GiB",
        cpu_offloading=None,
        worker_address=base_url.format(model_worker_port),
        controller_address=base_url.format(controller_port),
        limit_worker_concurrency=5,
        stream_interval=2,
        no_register=False,
):
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.model_worker import app, GptqConfig, ModelWorker, worker_id
    from fastchat.serve import model_worker
    import argparse

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    args.model_path = model_path
    args.model_names = model_names
    args.device = device
    args.load_8bit = load_8bit
    args.gptq_ckpt = gptq_ckpt
    args.gptq_wbits = gptq_wbits
    args.gptq_groupsize = gptq_groupsize
    args.gptq_act_order = gptq_act_order
    args.gpus = gpus
    args.num_gpus = num_gpus
    args.max_gpu_memory = max_gpu_memory
    args.cpu_offloading = cpu_offloading
    args.worker_address = worker_address
    args.controller_address = controller_address
    args.limit_worker_concurrency = limit_worker_concurrency
    args.stream_interval = stream_interval
    args.no_register = no_register

    if args.gpus:
        if len(args.gpus.split(",")) < args.num_gpus:
            raise ValueError(
                f"Larger --num-gpus ({args.num_gpus}) than --gpus {args.gpus}!"
            )
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpus

    if gpus and num_gpus is None:
        num_gpus = len(gpus.split(','))
    args.num_gpus = num_gpus

    gptq_config = GptqConfig(
        ckpt=gptq_ckpt or model_path,
        wbits=args.gptq_wbits,
        groupsize=args.gptq_groupsize,
        act_order=args.gptq_act_order,
    )
    # torch.multiprocessing.set_start_method('spawn')
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
        stream_interval=args.stream_interval,
    )

    sys.modules["fastchat.serve.model_worker"].worker = worker
    sys.modules["fastchat.serve.model_worker"].args = args
    sys.modules["fastchat.serve.model_worker"].gptq_config = gptq_config
    
    return app


def create_openai_api_app(
        host=host_ip,
        port=openai_api_port,
        controller_address=base_url.format(controller_port),
        api_keys=[],
):
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.openai_api_server import app, CORSMiddleware, app_settings

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app_settings.controller_address = controller_address
    app_settings.api_keys = api_keys

    return app


def run_controller(q):
    import uvicorn
    app = create_controller_app()

    @app.on_event("startup")
    async def on_startup():
        set_httpx_timeout()
        q.put(1)

    uvicorn.run(app, host=host_ip, port=controller_port)


def run_model_worker(q, *args, **kwargs):
    import uvicorn
    app = create_model_worker_app(*args, **kwargs)

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


if __name__ == "__main__":
    logger.info(llm_model_dict[LLM_MODEL])
    model_path = llm_model_dict[LLM_MODEL]["local_model_path"]

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

        # cuda 没办法用在fork的多进程中
        # model_worker_process = Process(
        #     target=run_model_worker,
        #     name=f"model_worker({os.getpid()})",
        #     args=(queue,),
        #     # kwargs={"load_8bit": True},
        #     daemon=True,
        # )
        # model_worker_process.start()

        openai_api_process = Process(
            target=run_openai_api,
            name=f"openai_api({os.getpid()})",
            args=(queue,),
            daemon=True,
        )
        openai_api_process.start()

        run_model_worker(queue)

        controller_process.join()
        # model_worker_process.join()
        openai_api_process.join()

# 服务启动后接口调用示例：
# import openai
# openai.api_key = "EMPTY" # Not support yet
# openai.api_base = "http://localhost:8888/v1"

# model = "chatglm2-6b"

# # create a chat completion
# completion = openai.ChatCompletion.create(
#   model=model,
#   messages=[{"role": "user", "content": "Hello! What is your name?"}]
# )
# # print the completion
# print(completion.choices[0].message.content)

from multiprocessing import Process, Queue
import multiprocessing as mp
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs.model_config import llm_model_dict, LLM_MODEL, LOG_PATH, logger
from server.utils import MakeFastAPIOffline, set_httpx_timeout, llm_device


host_ip = "0.0.0.0"
controller_port = 20001
model_worker_port = 20002
openai_api_port = 8888
base_url = "http://127.0.0.1:{}"


def create_controller_app(
        dispatch_method="shortest_queue",
):
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.controller import app, Controller

    controller = Controller(dispatch_method)
    sys.modules["fastchat.serve.controller"].controller = controller

    MakeFastAPIOffline(app)
    app.title = "FastChat Controller"
    return app


def create_model_worker_app(
        worker_address=base_url.format(model_worker_port),
        controller_address=base_url.format(controller_port),
        model_path=llm_model_dict[LLM_MODEL].get("local_model_path"),
        device=llm_device(),
        gpus=None,
        max_gpu_memory="20GiB",
        load_8bit=False,
        cpu_offloading=None,
        gptq_ckpt=None,
        gptq_wbits=16,
        gptq_groupsize=-1,
        gptq_act_order=False,
        awq_ckpt=None,
        awq_wbits=16,
        awq_groupsize=-1,
        model_names=[LLM_MODEL],
        num_gpus=1, # not in fastchat
        conv_template=None,
        limit_worker_concurrency=5,
        stream_interval=2,
        no_register=False,
):
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.model_worker import app, GptqConfig, AWQConfig, ModelWorker, worker_id
    import argparse
    import threading
    import fastchat.serve.model_worker

    # workaround to make program exit with Ctrl+c
    # it should be deleted after pr is merged by fastchat
    def _new_init_heart_beat(self):
        self.register_to_controller()
        self.heart_beat_thread = threading.Thread(
            target=fastchat.serve.model_worker.heart_beat_worker, args=(self,), daemon=True,
        )
        self.heart_beat_thread.start()
    ModelWorker.init_heart_beat = _new_init_heart_beat

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
    args.awq_ckpt = awq_ckpt
    args.awq_wbits = awq_wbits
    args.awq_groupsize = awq_groupsize
    args.gpus = gpus
    args.num_gpus = num_gpus
    args.max_gpu_memory = max_gpu_memory
    args.cpu_offloading = cpu_offloading
    args.worker_address = worker_address
    args.controller_address = controller_address
    args.conv_template = conv_template
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
    awq_config = AWQConfig(
        ckpt=args.awq_ckpt or args.model_path,
        wbits=args.awq_wbits,
        groupsize=args.awq_groupsize,
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
        awq_config=awq_config,
        stream_interval=args.stream_interval,
        conv_template=args.conv_template,
    )

    sys.modules["fastchat.serve.model_worker"].worker = worker
    sys.modules["fastchat.serve.model_worker"].args = args
    sys.modules["fastchat.serve.model_worker"].gptq_config = gptq_config
    
    MakeFastAPIOffline(app)
    app.title = f"FastChat LLM Server ({LLM_MODEL})"
    return app


def create_openai_api_app(
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

    MakeFastAPIOffline(app)
    app.title = "FastChat OpeanAI API Server"
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
    mp.set_start_method("spawn")
    queue = Queue()
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

        model_worker_process = Process(
            target=run_model_worker,
            name=f"model_worker({os.getpid()})",
            args=(queue,),
            # kwargs={"load_8bit": True},
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

        try:
            model_worker_process.join()
            controller_process.join()
            openai_api_process.join()
        except KeyboardInterrupt:
            model_worker_process.terminate()
            controller_process.terminate()
            openai_api_process.terminate()

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

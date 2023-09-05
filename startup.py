import asyncio
import multiprocessing as mp
import os
import subprocess
import sys
from multiprocessing import Process, Queue
from pprint import pprint

# 设置numexpr最大线程数，默认为CPU核心数
try:
    import numexpr

    n_cores = numexpr.utils.detect_number_of_cores()
    os.environ["NUMEXPR_MAX_THREADS"] = str(n_cores)
except:
    pass

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs.model_config import EMBEDDING_MODEL, llm_model_dict, LLM_MODEL, LOG_PATH, \
    logger
from configs.server_config import (WEBUI_SERVER, API_SERVER, FSCHAT_CONTROLLER,
                                   FSCHAT_OPENAI_API, )
from server.utils import (fschat_controller_address, fschat_model_worker_address,
                          fschat_openai_api_address, set_httpx_timeout,
                          get_model_worker_config, get_all_model_worker_configs,
                          MakeFastAPIOffline, FastAPI, llm_device, embedding_device)
import argparse
from typing import Tuple, List, Dict
from configs import VERSION


def create_controller_app(
        dispatch_method: str,
        log_level: str = "INFO",
) -> FastAPI:
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.controller import app, Controller, logger
    logger.setLevel(log_level)

    controller = Controller(dispatch_method)
    sys.modules["fastchat.serve.controller"].controller = controller

    MakeFastAPIOffline(app)
    app.title = "FastChat Controller"
    app._controller = controller
    return app


def create_model_worker_app(log_level: str = "INFO", **kwargs) -> Tuple[argparse.ArgumentParser, FastAPI]:
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.model_worker import app, GptqConfig, AWQConfig, ModelWorker, worker_id, logger
    import argparse
    import threading
    import fastchat.serve.model_worker
    logger.setLevel(log_level)

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
    args = parser.parse_args([])
    # default args. should be deleted after pr is merged by fastchat
    args.gpus = None
    args.max_gpu_memory = "20GiB"
    args.load_8bit = False
    args.cpu_offloading = None
    args.gptq_ckpt = None
    args.gptq_wbits = 16
    args.gptq_groupsize = -1
    args.gptq_act_order = False
    args.awq_ckpt = None
    args.awq_wbits = 16
    args.awq_groupsize = -1
    args.num_gpus = 1
    args.model_names = []
    args.conv_template = None
    args.limit_worker_concurrency = 5
    args.stream_interval = 2
    args.no_register = False

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

    # 在线模型API
    if worker_class := kwargs.get("worker_class"):
        worker = worker_class(model_names=args.model_names,
                              controller_addr=args.controller_address,
                              worker_addr=args.worker_address)
    # 本地模型
    else:
        # workaround to make program exit with Ctrl+c
        # it should be deleted after pr is merged by fastchat
        def _new_init_heart_beat(self):
            self.register_to_controller()
            self.heart_beat_thread = threading.Thread(
                target=fastchat.serve.model_worker.heart_beat_worker, args=(self,), daemon=True,
            )
            self.heart_beat_thread.start()

        ModelWorker.init_heart_beat = _new_init_heart_beat

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
        )
        sys.modules["fastchat.serve.model_worker"].args = args
        sys.modules["fastchat.serve.model_worker"].gptq_config = gptq_config

    sys.modules["fastchat.serve.model_worker"].worker = worker

    MakeFastAPIOffline(app)
    app.title = f"FastChat LLM Server ({args.model_names[0]})"
    app._worker = worker
    return app


def create_openai_api_app(
        controller_address: str,
        api_keys: List = [],
        log_level: str = "INFO",
) -> FastAPI:
    import fastchat.constants
    fastchat.constants.LOGDIR = LOG_PATH
    from fastchat.serve.openai_api_server import app, CORSMiddleware, app_settings
    from fastchat.utils import build_logger
    logger = build_logger("openai_api", "openai_api.log")
    logger.setLevel(log_level)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    sys.modules["fastchat.serve.openai_api_server"].logger = logger
    app_settings.controller_address = controller_address
    app_settings.api_keys = api_keys

    MakeFastAPIOffline(app)
    app.title = "FastChat OpeanAI API Server"
    return app


def _set_app_seq(app: FastAPI, q: Queue, run_seq: int):
    if q is None or not isinstance(run_seq, int):
        return

    if run_seq == 1:
        @app.on_event("startup")
        async def on_startup():
            set_httpx_timeout()
            q.put(run_seq)
    elif run_seq > 1:
        @app.on_event("startup")
        async def on_startup():
            set_httpx_timeout()
            while True:
                no = q.get()
                if no != run_seq - 1:
                    q.put(no)
                else:
                    break
            q.put(run_seq)


def run_controller(q: Queue, run_seq: int = 1, log_level: str = "INFO", e: mp.Event = None):
    import uvicorn
    import httpx
    from fastapi import Body
    import time
    import sys

    app = create_controller_app(
        dispatch_method=FSCHAT_CONTROLLER.get("dispatch_method"),
        log_level=log_level,
    )
    _set_app_seq(app, q, run_seq)

    @app.on_event("startup")
    def on_startup():
        if e is not None:
            e.set()

    # add interface to release and load model worker
    @app.post("/release_worker")
    def release_worker(
            model_name: str = Body(..., description="要释放模型的名称", samples=["chatglm-6b"]),
            # worker_address: str = Body(None, description="要释放模型的地址，与名称二选一", samples=[fschat_controller_address()]),
            new_model_name: str = Body(None, description="释放后加载该模型"),
            keep_origin: bool = Body(False, description="不释放原模型，加载新模型")
    ) -> Dict:
        available_models = app._controller.list_models()
        if new_model_name in available_models:
            msg = f"要切换的LLM模型 {new_model_name} 已经存在"
            logger.info(msg)
            return {"code": 500, "msg": msg}

        if new_model_name:
            logger.info(f"开始切换LLM模型：从 {model_name} 到 {new_model_name}")
        else:
            logger.info(f"即将停止LLM模型： {model_name}")

        if model_name not in available_models:
            msg = f"the model {model_name} is not available"
            logger.error(msg)
            return {"code": 500, "msg": msg}

        worker_address = app._controller.get_worker_address(model_name)
        if not worker_address:
            msg = f"can not find model_worker address for {model_name}"
            logger.error(msg)
            return {"code": 500, "msg": msg}

        r = httpx.post(worker_address + "/release",
                       json={"new_model_name": new_model_name, "keep_origin": keep_origin})
        if r.status_code != 200:
            msg = f"failed to release model: {model_name}"
            logger.error(msg)
            return {"code": 500, "msg": msg}

        if new_model_name:
            timer = 300  # wait 5 minutes for new model_worker register
            while timer > 0:
                models = app._controller.list_models()
                if new_model_name in models:
                    break
                time.sleep(1)
                timer -= 1
            if timer > 0:
                msg = f"sucess change model from {model_name} to {new_model_name}"
                logger.info(msg)
                return {"code": 200, "msg": msg}
            else:
                msg = f"failed change model from {model_name} to {new_model_name}"
                logger.error(msg)
                return {"code": 500, "msg": msg}
        else:
            msg = f"sucess to release model: {model_name}"
            logger.info(msg)
            return {"code": 200, "msg": msg}

    host = FSCHAT_CONTROLLER["host"]
    port = FSCHAT_CONTROLLER["port"]

    if log_level == "ERROR":
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    uvicorn.run(app, host=host, port=port, log_level=log_level.lower())


def run_model_worker(
        model_name: str = LLM_MODEL,
        controller_address: str = "",
        q: Queue = None,
        run_seq: int = 2,
        log_level: str = "INFO",
):
    import uvicorn
    from fastapi import Body
    import sys

    kwargs = get_model_worker_config(model_name)
    host = kwargs.pop("host")
    port = kwargs.pop("port")
    kwargs["model_names"] = [model_name]
    kwargs["controller_address"] = controller_address or fschat_controller_address()
    kwargs["worker_address"] = fschat_model_worker_address(model_name)
    model_path = kwargs.get("local_model_path", "")
    kwargs["model_path"] = model_path

    app = create_model_worker_app(log_level=log_level, **kwargs)
    _set_app_seq(app, q, run_seq)
    if log_level == "ERROR":
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    # add interface to release and load model
    @app.post("/release")
    def release_model(
            new_model_name: str = Body(None, description="释放后加载该模型"),
            keep_origin: bool = Body(False, description="不释放原模型，加载新模型")
    ) -> Dict:
        if keep_origin:
            if new_model_name:
                q.put(["start", new_model_name])
        else:
            if new_model_name:
                q.put(["replace", new_model_name])
            else:
                q.put(["stop"])
        return {"code": 200, "msg": "done"}

    uvicorn.run(app, host=host, port=port, log_level=log_level.lower())


def run_openai_api(q: Queue, run_seq: int = 3, log_level: str = "INFO"):
    import uvicorn
    import sys

    controller_addr = fschat_controller_address()
    app = create_openai_api_app(controller_addr, log_level=log_level)  # TODO: not support keys yet.
    _set_app_seq(app, q, run_seq)

    host = FSCHAT_OPENAI_API["host"]
    port = FSCHAT_OPENAI_API["port"]
    if log_level == "ERROR":
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    uvicorn.run(app, host=host, port=port)


def run_api_server(q: Queue, run_seq: int = 4):
    from server.api import create_app
    import uvicorn

    app = create_app()
    _set_app_seq(app, q, run_seq)

    host = API_SERVER["host"]
    port = API_SERVER["port"]

    uvicorn.run(app, host=host, port=port)


def run_webui(q: Queue, run_seq: int = 5):
    host = WEBUI_SERVER["host"]
    port = WEBUI_SERVER["port"]

    if q is not None and isinstance(run_seq, int):
        while True:
            no = q.get()
            if no != run_seq - 1:
                q.put(no)
            else:
                break
        q.put(run_seq)
    p = subprocess.Popen(["streamlit", "run", "webui.py",
                          "--server.address", host,
                          "--server.port", str(port)])
    p.wait()


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--all-webui",
        action="store_true",
        help="run fastchat's controller/openai_api/model_worker servers, run api.py and webui.py",
        dest="all_webui",
    )
    parser.add_argument(
        "--all-api",
        action="store_true",
        help="run fastchat's controller/openai_api/model_worker servers, run api.py",
        dest="all_api",
    )
    parser.add_argument(
        "--llm-api",
        action="store_true",
        help="run fastchat's controller/openai_api/model_worker servers",
        dest="llm_api",
    )
    parser.add_argument(
        "-o",
        "--openai-api",
        action="store_true",
        help="run fastchat's controller/openai_api servers",
        dest="openai_api",
    )
    parser.add_argument(
        "-m",
        "--model-worker",
        action="store_true",
        help="run fastchat's model_worker server with specified model name. specify --model-name if not using default LLM_MODEL",
        dest="model_worker",
    )
    parser.add_argument(
        "-n",
        "--model-name",
        type=str,
        default=LLM_MODEL,
        help="specify model name for model worker.",
        dest="model_name",
    )
    parser.add_argument(
        "-c",
        "--controller",
        type=str,
        help="specify controller address the worker is registered to. default is server_config.FSCHAT_CONTROLLER",
        dest="controller_address",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="run api.py server",
        dest="api",
    )
    parser.add_argument(
        "-p",
        "--api-worker",
        action="store_true",
        help="run online model api such as zhipuai",
        dest="api_worker",
    )
    parser.add_argument(
        "-w",
        "--webui",
        action="store_true",
        help="run webui.py server",
        dest="webui",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="减少fastchat服务log信息",
        dest="quiet",
    )
    args = parser.parse_args()
    return args, parser


def dump_server_info(after_start=False, args=None):
    import platform
    import langchain
    import fastchat
    from server.utils import api_address, webui_address

    print("\n")
    print("=" * 30 + "Langchain-Chatchat Configuration" + "=" * 30)
    print(f"操作系统：{platform.platform()}.")
    print(f"python版本：{sys.version}")
    print(f"项目版本：{VERSION}")
    print(f"langchain版本：{langchain.__version__}. fastchat版本：{fastchat.__version__}")
    print("\n")

    model = LLM_MODEL
    if args and args.model_name:
        model = args.model_name
    print(f"当前LLM模型：{model} @ {llm_device()}")
    pprint(llm_model_dict[model])
    print(f"当前Embbedings模型： {EMBEDDING_MODEL} @ {embedding_device()}")

    if after_start:
        print("\n")
        print(f"服务端运行信息：")
        if args.openai_api:
            print(f"    OpenAI API Server: {fschat_openai_api_address()}/v1")
            print("     (请确认llm_model_dict中配置的api_base_url与上面地址一致。)")
        if args.api:
            print(f"    Chatchat  API  Server: {api_address()}")
        if args.webui:
            print(f"    Chatchat WEBUI Server: {webui_address()}")
    print("=" * 30 + "Langchain-Chatchat Configuration" + "=" * 30)
    print("\n")


async def start_main_server():
    import time
    import signal

    def handler(signalname):
        """
        Python 3.9 has `signal.strsignal(signalnum)` so this closure would not be needed.
        Also, 3.8 includes `signal.valid_signals()` that can be used to create a mapping for the same purpose.
        """
        def f(signal_received, frame):
            raise KeyboardInterrupt(f"{signalname} received")
        return f

    # This will be inherited by the child process if it is forked (not spawned)
    signal.signal(signal.SIGINT, handler("SIGINT"))
    signal.signal(signal.SIGTERM, handler("SIGTERM"))

    mp.set_start_method("spawn")
    manager = mp.Manager()

    queue = manager.Queue()
    args, parser = parse_args()

    if args.all_webui:
        args.openai_api = True
        args.model_worker = True
        args.api = True
        args.api_worker = True
        args.webui = True

    elif args.all_api:
        args.openai_api = True
        args.model_worker = True
        args.api = True
        args.api_worker = True
        args.webui = False

    elif args.llm_api:
        args.openai_api = True
        args.model_worker = True
        args.api_worker = True
        args.api = False
        args.webui = False

    dump_server_info(args=args)

    if len(sys.argv) > 1:
        logger.info(f"正在启动服务：")
        logger.info(f"如需查看 llm_api 日志，请前往 {LOG_PATH}")

    processes = {"online-api": []}

    def process_count():
        return len(processes) + len(processes["online-api"]) - 1

    if args.quiet:
        log_level = "ERROR"
    else:
        log_level = "INFO"

    controller_started = manager.Event()
    if args.openai_api:
        process = Process(
            target=run_controller,
            name=f"controller",
            args=(queue, process_count() + 1, log_level, controller_started),
            daemon=True,
        )

        processes["controller"] = process

        process = Process(
            target=run_openai_api,
            name=f"openai_api",
            args=(queue, process_count() + 1),
            daemon=True,
        )
        processes["openai_api"] = process

    if args.model_worker:
        config = get_model_worker_config(args.model_name)
        if not config.get("online_api"):
            process = Process(
                target=run_model_worker,
                name=f"model_worker - {args.model_name}",
                args=(args.model_name, args.controller_address, queue, process_count() + 1, log_level),
                daemon=True,
            )

            processes["model_worker"] = process

    if args.api_worker:
        configs = get_all_model_worker_configs()
        for model_name, config in configs.items():
            if config.get("online_api") and config.get("worker_class"):
                process = Process(
                    target=run_model_worker,
                    name=f"model_worker - {model_name}",
                    args=(model_name, args.controller_address, queue, process_count() + 1, log_level),
                    daemon=True,
                )

                processes["online-api"].append(process)

    if args.api:
        process = Process(
            target=run_api_server,
            name=f"API Server",
            args=(queue, process_count() + 1),
            daemon=True,
        )

        processes["api"] = process

    if args.webui:
        process = Process(
            target=run_webui,
            name=f"WEBUI Server",
            args=(queue, process_count() + 1),
            daemon=True,
        )

        processes["webui"] = process

    if process_count() == 0:
        parser.print_help()
    else:
        try:
            # 保证任务收到SIGINT后，能够正常退出
            if p:= processes.get("controller"):
                p.start()
                p.name = f"{p.name} ({p.pid})"
                controller_started.wait()

            if p:= processes.get("openai_api"):
                p.start()
                p.name = f"{p.name} ({p.pid})"

            if p:= processes.get("model_worker"):
                p.start()
                p.name = f"{p.name} ({p.pid})"

            for p in processes.get("online-api", []):
                p.start()
                p.name = f"{p.name} ({p.pid})"

            if p:= processes.get("api"):
                p.start()
                p.name = f"{p.name} ({p.pid})"

            if p:= processes.get("webui"):
                p.start()
                p.name = f"{p.name} ({p.pid})"

            while True:
                no = queue.get()
                if no == process_count():
                    time.sleep(0.5)
                    dump_server_info(after_start=True, args=args)
                    break
                else:
                    queue.put(no)

            if model_worker_process := processes.get("model_worker"):
                model_worker_process.join()
            for process in processes.get("online-api", []):
                process.join()
            for name, process in processes.items():
                if name not in ["model_worker", "online-api"]:
                    if isinstance(p, list):
                        for work_process in p:
                            work_process.join()
                    else:
                        process.join()
        except Exception as e:
            # if model_worker_process := processes.pop("model_worker", None):
            #     model_worker_process.terminate()
            # for process in processes.pop("online-api", []):
            #     process.terminate()
            # for process in processes.values():
            #
            #     if isinstance(process, list):
            #         for work_process in process:
            #             work_process.terminate()
            #     else:
            #         process.terminate()
            logger.error(e)
            logger.warning("Caught KeyboardInterrupt! Setting stop event...")
        finally:
            # Send SIGINT if process doesn't exit quickly enough, and kill it as last resort
            # .is_alive() also implicitly joins the process (good practice in linux)
            # while alive_procs := [p for p in processes.values() if p.is_alive()]:

            for p in processes.values():
                logger.warning("Sending SIGKILL to %s", p)
                # Queues and other inter-process communication primitives can break when
                # process is killed, but we don't care here

                if isinstance(p, list):
                    for process in p:
                        process.kill()

                else:
                    p.kill()

            for p in processes.values():
                logger.info("Process status: %s", p)

if __name__ == "__main__":

    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
    # 同步调用协程代码
    loop.run_until_complete(start_main_server())


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

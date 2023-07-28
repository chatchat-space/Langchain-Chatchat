import sys
import os
from configs.model_config import (
    llm_model_dict,
    LLM_MODEL,
    EMBEDDING_DEVICE,
    LLM_DEVICE,
    LOG_PATH,
    logger,
)
from fastchat.serve.model_worker import heart_beat_worker
from fastapi import FastAPI
import threading
import asyncio

# 把fastchat的3个服务端整合在一起，分别是：
# - http://{host_ip}:{port}/controller     对应 python -m fastchat.serve.controller
# - http://{host_ip}:{port}/model_worker   对应 python -m fastchat.serve.model_worker ...
# - http://{host_ip}:{port}/openai         对应 python -m fastchat.serve.openai_api_server ...


host_ip = "0.0.0.0"
port = 8888
base_url = f"http://127.0.0.1:{port}"


def create_controller_app(
    dispatch_method="shortest_queue",
):
    from fastchat.serve.controller import app, Controller
    controller = Controller(dispatch_method)
    sys.modules["fastchat.serve.controller"].controller = controller
    logger.info(f"controller dispatch method: {dispatch_method}")
    return app, controller


def create_model_worker_app(
    model_path,
    model_names=[LLM_MODEL],
    device=LLM_DEVICE,
    load_8bit=False,
    gptq_ckpt=None,
    gptq_wbits=16,
    gpus='',
    num_gpus=-1,
    max_gpu_memory=-1,
    cpu_offloading=None,
    worker_address=f"{base_url}/model_worker",
    controller_address=f"{base_url}/controller",
    limit_model_concurrency=5,
    stream_interval=2,
    no_register=True, # mannually register
):
    from fastchat.serve.model_worker import app, GptqConfig, ModelWorker, worker_id
    from fastchat.serve import model_worker
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
    return app, worker


def create_openai_api_app(
    host=host_ip,
    port=port,
    controller_address=f"{base_url}/controller",
    allow_credentials=None,
    allowed_origins=["*"],
    allowed_methods=["*"],
    allowed_headers=["*"],
    api_keys=[],
):
    from fastchat.serve.openai_api_server import app, CORSMiddleware, app_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
    )
    app_settings.controller_address = controller_address
    app_settings.api_keys = api_keys
    sys.modules["fastchat.serve.openai_api_server.app_settings"] = app_settings

    return app


LLM_MODEL = 'chatglm-6b'
model_path = llm_model_dict[LLM_MODEL]["local_model_path"]
global controller


if not model_path:
    logger.error("local_model_path 不能为空")
else:
    logger.info(f"using local model: {model_path}")
    app = FastAPI()

    controller_app, controller = create_controller_app()
    app.mount("/controller", controller_app)

    model_woker_app, worker = create_model_worker_app(model_path)
    app.mount("/model_worker", model_woker_app)

    openai_api_app = create_openai_api_app()
    app.mount("/openai", openai_api_app)


    @app.on_event("startup")
    async def on_startup():
        logger.info("Register to controller")
        controller.register_worker(
            worker.worker_addr,
            True,
            worker.get_status(),
        )
        worker.heart_beat_thread = threading.Thread(
            target=heart_beat_worker, args=(worker,)
        )
        worker.heart_beat_thread.start()

        # 通过网络请求注册会卡死
        # async def register():
        #     while True:
        #         try:
        #             worker.register_to_controller()
        #             worker.heart_beat_thread = threading.Thread(
        #                 target=heart_beat_worker, args=(worker,)
        #             )
        #             worker.heart_beat_thread.start()
        #         except:
        #             await asyncio.sleep(1)
        # asyncio.get_event_loop().create_task(register())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=host_ip, port=port)

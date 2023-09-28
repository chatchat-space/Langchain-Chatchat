from server.model_workers.base import ApiModelWorker
from fastchat import conversation as conv
import sys
import json
from server.model_workers import SparkApi
import websockets
from server.utils import iter_over_async, asyncio
from typing import List


async def request(appid, api_key, api_secret, Spark_url,domain, question, temperature):
    # print("星火:")
    wsParam = SparkApi.Ws_Param(appid, api_key, api_secret, Spark_url)
    wsUrl = wsParam.create_url()
    data = SparkApi.gen_params(appid, domain, question, temperature)
    async with websockets.connect(wsUrl) as ws:
        await ws.send(json.dumps(data, ensure_ascii=False))
        finish = False
        while not finish:
             chunk = await ws.recv()
             response = json.loads(chunk)
             if response.get("header", {}).get("status") == 2:
                 finish = True
             if text := response.get("payload", {}).get("choices", {}).get("text"):
                yield text[0]["content"]


class XingHuoWorker(ApiModelWorker):
    def __init__(
        self,
        *,
        model_names: List[str] = ["xinghuo-api"],
        controller_addr: str,
        worker_addr: str,
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 8192)
        super().__init__(**kwargs)

        # TODO: 确认模板是否需要修改
        self.conv = conv.Conversation(
            name=self.model_names[0],
            system_message="",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )

    def generate_stream_gate(self, params):
        # TODO: 当前每次对话都要重新连接websocket，确认是否可以保持连接

        super().generate_stream_gate(params)
        config = self.get_config()
        appid = config.get("APPID")
        api_secret = config.get("APISecret")
        api_key = config.get("api_key")

        if config.get("is_v2"):
            domain = "generalv2"    # v2.0版本
            Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址
        else:
            domain = "general"   # v1.5版本
            Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址

        question = self.prompt_to_messages(params["prompt"])
        text = ""

        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()

        for chunk in iter_over_async(
             request(appid, api_key, api_secret, Spark_url, domain, question, params.get("temperature")),
             loop=loop,
        ):
            if chunk:
                print(chunk)
                text += chunk
                yield json.dumps({"error_code": 0, "text": text}, ensure_ascii=False).encode() + b"\0"
    
    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = XingHuoWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21003",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21003)

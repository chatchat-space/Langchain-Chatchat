import zhipuai
from server.utils import MakeFastAPIOffline
from fastchat.serve.model_worker import app
from server.model_workers.base import ApiModelWorker
from server.utils import get_model_worker_config
import sys


class ChatGLMWorker(ApiModelWorker):
    BASE_URL = "https://open.bigmodel.cn/api/paas/v3/model-api"
    SUPPORT_MODELS = ["chatglm_pro", "chatglm_std", "chatglm_lite"]

    def __init__(self, **kwargs):
        super().__init__(model_name="chatglm-api", context_len=32768, **kwargs)
        self.init_heart_beat()

    def generate_stream_gate(self, params):
        # TODO: 支持stream参数，维护request_id，传过来的prompt也有问题
        super().generate_stream_gate(params)
        zhipuai.api_key = get_model_worker_config("chatglm-api").get("api_key")

        response = zhipuai.model_api.sse_invoke(
            model="chatglm_lite",
            prompt=[{"role": "user", "content": params["prompt"]}],
            top_p=params.get("top_p"),
            temperature=params.get("temperature"),
        )
        for e in response.events():
            if e.event == "add":
                print(e.data)
                yield {"error_code": 0, "text": e.data} # TODO: 需要兼容openai接口形式
            # elif e.event == "finish":
            #     ...
    
    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)


if __name__ == "__main__":
    import uvicorn

    worker = ChatGLMWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:20003",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20003)

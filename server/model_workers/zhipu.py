from fastchat.conversation import Conversation
from server.model_workers.base import *
from fastchat import conversation as conv
import sys
from typing import List, Dict, Iterator, Literal
from configs import logger, log_verbose


class ChatGLMWorker(ApiModelWorker):
    DEFAULT_EMBED_MODEL = "text_embedding"

    def __init__(
        self,
        *,
        model_names: List[str] = ["zhipu-api"],
        controller_addr: str = None,
        worker_addr: str = None,
        version: Literal["chatglm_turbo"] = "chatglm_turbo",
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 32768)
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Iterator[Dict]:
        # TODO: 维护request_id
        import zhipuai

        params.load_config(self.model_names[0])
        zhipuai.api_key = params.api_key

        if log_verbose:
            logger.info(f'{self.__class__.__name__}:params: {params}')

        response = zhipuai.model_api.sse_invoke(
            model=params.version,
            prompt=params.messages,
            temperature=params.temperature,
            top_p=params.top_p,
            incremental=False,
        )
        for e in response.events():
            if e.event == "add":
                yield {"error_code": 0, "text": e.data}
            elif e.event in ["error", "interrupted"]:
                data = {
                    "error_code": 500,
                    "text": e.data,
                    "error": {
                        "message": e.data,
                        "type": "invalid_request_error",
                        "param": None,
                        "code": None,
                    }
                }
                self.logger.error(f"请求智谱 API 时发生错误：{data}")
                yield data

    def do_embeddings(self, params: ApiEmbeddingsParams) -> Dict:
        import zhipuai

        params.load_config(self.model_names[0])
        zhipuai.api_key = params.api_key

        embeddings = []
        try:
            for t in params.texts:
                response = zhipuai.model_api.invoke(model=params.embed_model or self.DEFAULT_EMBED_MODEL, prompt=t)
                if response["code"] == 200:
                    embeddings.append(response["data"]["embedding"])
                else:
                    self.logger.error(f"请求智谱 API 时发生错误：{response}")
                    return response  # dict with code & msg
        except Exception as e:
            self.logger.error(f"请求智谱 API 时发生错误：{data}")
            data = {"code": 500, "msg": f"对文本向量化时出错：{e}"}
            return data

        return {"code": 200, "data": embeddings}

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        # print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        # 这里的是chatglm api的模板，其它API的conv_template需要定制
        return conv.Conversation(
            name=self.model_names[0],
            system_message="你是一个聪明的助手，请根据用户的提示来完成任务",
            messages=[],
            roles=["Human", "Assistant", "System"],
            sep="\n###",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = ChatGLMWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21001)

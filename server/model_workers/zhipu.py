import zhipuai
from server.model_workers.base import ApiModelWorker
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal,Dict


class ChatGLMWorker(ApiModelWorker):
    BASE_URL = "https://open.bigmodel.cn/api/paas/v3/model-api"
    SUPPORT_MODELS = ["chatglm_pro", "chatglm_std", "chatglm_lite"]

    def __init__(
        self,
        *,
        model_names: List[str] = ["chatglm-api"],
        version: Literal["chatglm_pro", "chatglm_std", "chatglm_lite"] = "chatglm_std",
        controller_addr: str,
        worker_addr: str,
        **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 32768)
        super().__init__(**kwargs)
        self.version = version
        self.zhipuai = zhipuai
        from server.utils import get_model_worker_config
        self.zhipuai.api_key = get_model_worker_config("chatglm-api").get("api_key")
        # 这里的是chatglm api的模板，其它API的conv_template需要定制
        self.conv = conv.Conversation(
            name="chatglm-api",
            system_message="你是一个聪明、对人类有帮助的人工智能，你可以对人类提出的问题给出有用、详细、礼貌的回答。",
            messages=[],
            roles=["Human", "Assistant"],
            sep="\n### ",
            stop_str="###",
        )

    def generate_stream_gate(self, params):
        # TODO: 支持stream参数，维护request_id，传过来的prompt也有问题
        super().generate_stream_gate(params)

        model=self.version
        # if isinstance(params["prompt"], str):
        #     prompt=self.prompt_collator(content_user=params["prompt"],
        #                                 role_user="user") #[{"role": "user", "content": params["prompt"]}]
        # else:
        #     prompt = params["prompt"]
        prompt = params["prompt"]
        print(prompt)
        temperature=params.get("temperature")
        top_p=params.get("top_p")
        stream = params.get("stream")

        if stream:
            return self.create_stream(model=model,
                                    message=prompt,
                                    top_p=top_p,
                                    temperature=temperature)
        else:
            return self.create_oneshot(model=model,
                                        message=prompt,
                                        top_p=top_p,
                                        temperature=temperature)

        # response = zhipuai.model_api.sse_invoke(
        #     model=self.version,
        #     prompt=[{"role": "user", "content": params["prompt"]}],
        #     temperature=params.get("temperature"),
        #     top_p=params.get("top_p"),
        #     incremental=False,
        # )
        # for e in response.events():
        #     if e.event == "add":
        #         yield json.dumps({"error_code": 0, "text": e.data}, ensure_ascii=False).encode() + b"\0"
        #     # TODO: 更健壮的消息处理
        #     # elif e.event == "finish":
        #     #     ...
    
    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)

    def create_oneshot(self,
                    message: List[Dict[str,str]]=[{"role":"user","content":"你好，你可以做什么"}],
                    model:str = "chatglm_pro",
                    top_p:float=0.7,
                    temperature:float=0.9,
                    **kwargs
                    ):
            response = self.zhipuai.model_api.invoke(
                model = model,
                prompt = message,
                top_p = top_p,
                temperature = temperature
            )
            if response["code"] == 200:
                result = response["data"]["choices"][-1]["content"]
                return json.dumps({"error_code": 0, "text": result}, ensure_ascii=False).encode() + b"\0"
            else:
                #TODO 确认openai的error code
                print(f"error occurred, error code:{response['code']},error msg:{response['msg']}")
                return json.dumps({"error_code": response['code'], 
                                   "text": f"error occurred, error code:{response['code']},error msg:{response['msg']}"
                                   }, 
                                   ensure_ascii=False).encode() + b"\0"
            
    def create_stream(self,
                    message: List[Dict[str,str]]=[{"role":"user","content":"你好，你可以做什么"}],
                    model:str = "chatglm_pro",
                    top_p:float=0.7,
                    temperature:float=0.9,
                    **kwargs
                    ):
            response = self.zhipuai.model_api.sse_invoke(
                model = model,
                prompt = message,
                top_p = top_p,
                temperature = temperature,
                incremental = True
            )
            for event in response.events():
                if event.event == "add":
                    # yield event.data
                    yield json.dumps({"error_code": 0, "text": event.data}, ensure_ascii=False).encode() + b"\0"
                elif event.event == "error" or event.event == "interrupted":
                    # return event.data
                    yield json.dumps({"error_code": 0, "text": event.data}, ensure_ascii=False).encode() + b"\0"
                elif event.event == "finish":
                    # yield event.data
                    yield json.dumps({"error_code": 0, "text": event.data}, ensure_ascii=False).encode() + b"\0"
                    print(event.meta)
                else:
                    print("Something get wrong with ZhipuAPILoader.create_chat_completion_stream")
                    print(event.data)
                    yield json.dumps({"error_code": 1, "text": event.data}, ensure_ascii=False).encode() + b"\0"
               
    def create_chat_completion(self,
                               model: str = "chatglm_pro",
                               prompt:List[Dict[str,str]]=[{"role":"user","content":"你好，你可以做什么"}],
                                top_p:float=0.7,
                                temperature:float=0.9,
                                stream:bool=False):

        if stream:
            return self.create_stream(model=model,
                                    message=prompt,
                                    top_p=top_p,
                                    temperature=temperature)
        else:
            return self.create_oneshot(model=model,
                                        message=prompt,
                                        top_p=top_p,
                                        temperature=temperature)
        
    async def acreate_chat_completion(self,
                    prompt: List[Dict[str,str]]=[{"role":"system","content":"你是一个人工智能助手"},
                                            {"role":"user","content":"你好。"}],
                    model:str = "chatglm_pro",
                    top_p:float=0.7,
                    temperature:float=0.9,
                    **kwargs):
        response = await self.zhipuai.model_api.async_invoke(
                    model = model,
                    prompt = prompt,
                    top_p = top_p,
                    temperature = temperature
                    )

        if response["code"] == 200:
            task_id = response['data']['task_id']
            status = "PROCESSING"
            while status != "SUCCESS":
                # await asyncio.sleep(3) # 
                resp = self.zhipuai.model_api.query_async_invoke_result(task_id)
                status = resp['data']['task_status']
            return resp['data']['choices'][-1]['content']
        else:
            print(f"error occurred, error code:{response['code']},error msg:{response['msg']}")
            return 
        
    def create_completion(self,
                               prompt:str="你好",
                               model:str="chatglm_pro",
                               top_p:float=0.7,
                               temperature:float=0.9,
                               stream:bool=False,
                               **kwargs):
        message = self.prompt_collator(content_user=prompt)
        if stream:
            return self.create_stream(model=model,
                                    message=message,
                                    top_p=top_p,
                                    temperature=temperature)
        else:
            return self.create_oneshot(model=model,
                                    message=message,
                                    top_p=top_p,
                                    temperature=temperature)
    #? make it a sync function?    
    async def acreate_completion(self,
                    prompt:str="你好",
                    model:str = "chatglm_pro",
                    top_p:float=0.7,
                    temperature:float=0.9,
                    **kwargs):
        message = self.prompt_collator(content_user=prompt)
        response = self.zhipuai.model_api.async_invoke(
                    model = model,
                    prompt = message,
                    top_p = top_p,
                    temperature = temperature
                    )

        if response["code"] == 200:
            task_id = response['data']['task_id']
            status = "PROCESSING"
            while status != "SUCCESS":
                # await asyncio.sleep(3) # 
                resp = self.zhipuai.model_api.query_async_invoke_result(task_id)
                status = resp['data']['task_status']
            return resp['data']['choices'][-1]['content']
        else:
            print(f"error occurred, error code:{response['code']},error msg:{response['msg']}")
            return 


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.model_worker import app

    worker = ChatGLMWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:20003",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=20003)

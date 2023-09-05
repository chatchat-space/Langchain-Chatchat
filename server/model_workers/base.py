from configs.model_config import LOG_PATH
import fastchat.constants
fastchat.constants.LOGDIR = LOG_PATH
from fastchat.serve.model_worker import BaseModelWorker
import uuid
import json
import sys
from pydantic import BaseModel
import fastchat
import threading
from typing import Dict, List


# 恢复被fastchat覆盖的标准输出
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__


class ApiModelOutMsg(BaseModel):
    error_code: int = 0
    text: str

class ApiModelWorker(BaseModelWorker):
    BASE_URL: str
    SUPPORT_MODELS: List

    def __init__(
        self,
        model_names: List[str],
        controller_addr: str,
        worker_addr: str,
        context_len: int = 2048,
        **kwargs,
    ):
        kwargs.setdefault("worker_id", uuid.uuid4().hex[:8])
        kwargs.setdefault("model_path", "")
        kwargs.setdefault("limit_worker_concurrency", 5)
        super().__init__(model_names=model_names,
                        controller_addr=controller_addr,
                        worker_addr=worker_addr,
                        **kwargs)
        self.context_len = context_len
        self.init_heart_beat()

    def count_token(self, params):
        # TODO：需要完善
        print("count token")
        print(params)
        prompt = params["prompt"]
        return {"count": len(str(prompt)), "error_code": 0}

    def generate_stream_gate(self, params):
        self.call_ct += 1
    
    def generate_gate(self, params):
        for x in self.generate_stream_gate(params):
            pass
        return json.loads(x[:-1].decode())

    def get_embeddings(self, params):
        print("embedding")
        print(params)

    # workaround to make program exit with Ctrl+c
    # it should be deleted after pr is merged by fastchat
    def init_heart_beat(self):
        self.register_to_controller()
        self.heart_beat_thread = threading.Thread(
            target=fastchat.serve.model_worker.heart_beat_worker, args=(self,), daemon=True,
        )
        self.heart_beat_thread.start()

    def prompt_collator(self,
                        content_user: str = None,
                        role_user:str = "user",
                        content_assistant: str = None,
                        role_assistant: str = "assistant",
                        meta_prompt:List[Dict[str,str]] = [{"role":"system","content":"你是一个AI工具"}],
                        use_meta_prompt:bool=False):
        prompt = []
        if use_meta_prompt:
            prompt += meta_prompt
        if content_user:
            prompt_dict = {"role": role_user, "content":content_user}
            prompt.append(prompt_dict)
        if content_assistant:
            prompt_dict = {"role": role_assistant, "content":content_assistant}
            prompt.append(prompt_dict)
        return prompt

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
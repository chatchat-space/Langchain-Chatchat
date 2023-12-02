import sys
from fastchat.conversation import Conversation
from server.model_workers.base import *
from server.utils import get_httpx_client
from fastchat import conversation as conv
import json
from typing import List, Dict


class OpenaiWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            controller_addr: str,
            worker_addr: str,
            model_names: List[str] = ["openai-api"],
            version: str = "gpt-3.5-turbo",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384) 
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])
        data = dict(
            messages=params.messages,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            stream=True,
        )
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': params.api_key,
        }

        text = ""
        with get_httpx_client() as client:
            with client.stream("POST", url, headers=headers, json=data) as response:
                for line in response.iter_lines():
                    if not line.strip() or "[DONE]" in line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    resp = json.loads(line)
                    if choices := resp["choices"]:
                        if chunk := choices[0].get("delta", {}).get("content"):
                            text += chunk
                            yield {
                                    "error_code": 0,
                                    "text": text
                                }

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        return conv.Conversation(
            name=self.model_names[0],
            system_message="You are ChatGPT, a large language model trained by OpenAI.",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.base_model_worker import app

    worker = OpenaiWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21010",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21010)

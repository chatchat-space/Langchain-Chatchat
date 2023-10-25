import sys
from fastchat.conversation import Conversation
from server.model_workers.base import ApiModelWorker
from server.utils import get_model_worker_config, get_httpx_client
from fastchat import conversation as conv
import json
from typing import List, Dict
from configs import TEMPERATURE


def request_azure_api(
        messages: List[Dict[str, str]],
        resource_name: str = None,
        api_key: str = None,
        deployment_name: str = None,
        api_version: str = "2023-07-01-preview",
        temperature: float = TEMPERATURE,
        max_tokens: int = None,
        model_name: str = "azure-api",
):
    config = get_model_worker_config(model_name)
    data = dict(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    url = f"https://{resource_name}.openai.azure.com/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'api-key': api_key,
    }
    with get_httpx_client() as client:
        with client.stream("POST", url, headers=headers, json=data) as response:
            for line in response.iter_lines():
                if not line.strip() or "[DONE]" in line:
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                resp = json.loads(line)
                yield resp

class AzureWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            controller_addr: str,
            worker_addr: str,
            model_names: List[str] = ["azure-api"],
            version: str = "gpt-35-turbo",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 8192)
        super().__init__(**kwargs)

        config = self.get_config()

        self.resource_name = config.get("resource_name")
        self.api_key = config.get("api_key")
        self.api_version = config.get("api_version")
        self.version = version
        self.deployment_name = config.get("deployment_name")

    def generate_stream_gate(self, params):
        super().generate_stream_gate(params)

        messages = self.prompt_to_messages(params["prompt"])
        text = ""
        for resp in request_azure_api(messages=messages,
                                      resource_name=self.resource_name,
                                      api_key=self.api_key,
                                      api_version=self.api_version,
                                      deployment_name=self.deployment_name,
                                      temperature=params.get("temperature"),
                                      max_tokens=params.get("max_tokens")):
            if choices := resp["choices"]:
                if chunk := choices[0].get("delta", {}).get("content"):
                    text += chunk
                    yield json.dumps(
                        {
                            "error_code": 0,
                            "text": text
                        },
                        ensure_ascii=False
                    ).encode() + b"\0"

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        # TODO: 确认模板是否需要修改
        return conv.Conversation(
            name=self.model_names[0],
            system_message="",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.base_model_worker import app

    worker = AzureWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21008",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21008)

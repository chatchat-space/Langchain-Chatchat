import json
from server.model_workers.base import ApiModelWorker
from server.utils import get_model_worker_config
from fastchat import conversation as conv
import sys
import json
from typing import List, Literal, Dict
from configs import TEMPERATURE


AZURE_CONTEXT_LEN = {
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
}


def request_azure_api(
    messages: List[Dict[str, str]],
    api_base_url: str = None,
    api_proxy: str = None,
    api_key: str = None,
    version: str = "gpt-35-turbo",
    deployment_name: str = None,
    api_version: str = None,
    temperature: float = TEMPERATURE,
    max_tokens: int = None,
    model_name: str = "azure-api",
):
    import openai

    config = get_model_worker_config(model_name)
    api_base_url = api_base_url or config.get("api_base_url")
    api_proxy = api_proxy or config.get("api_proxy")
    api_key = api_key or config.get("api_key")
    api_version = api_version or config.get("api_version")
    version = version or config.get("version")
    deployment_name = deployment_name or config.get("deployment_name")

    openai.api_type = "azure"
    openai.api_version = api_version
    openai.api_base = api_base_url
    openai.proxy = api_proxy
    openai.api_key = api_key

    data = dict(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    if deployment_name: # deployment_name takes priority over engine(i.e. version)
        data.update({
            "deployment_id": deployment_name,
        })
    else:
        data.update({
            "engine": version,
        })

    for data in openai.ChatCompletion.create(**data):
        yield data


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
        kwargs.setdefault("context_len", AZURE_CONTEXT_LEN.get(version, min(AZURE_CONTEXT_LEN.values())))
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

        config = self.get_config()
        self.api_base_url = config.get("api_base_url")
        self.api_key = config.get("api_key")
        self.api_version = config.get("api_version")
        self.version = config.get("version")
        self.deployment_name = config.get("deployment_name")

    def generate_stream_gate(self, params):
        super().generate_stream_gate(params)

        messages = self.prompt_to_messages(params["prompt"])

        text = ""
        try:
            for resp in request_azure_api(messages=messages,
                                        api_base_url=self.api_base_url,
                                        api_key=self.api_key,
                                        version=self.version,
                                        api_version=self.api_version,
                                        deployment_name=self.deployment_name,
                                        temperature=params.get("temperature"),
                                        max_tokens=params.get("max_tokens")):
                if choices := resp.choices:
                    if chunk := choices[0].get("delta", {}).get("content"):
                        text += chunk
                        yield json.dumps(
                            {
                            "error_code": 0,
                            "text": text
                            },
                            ensure_ascii=False
                        ).encode() + b"\0"
        except Exception as e:
            yield json.dumps(
                {
                "error_code": 500,
                "text": str(e)
                },
                ensure_ascii=False
            ).encode() + b"\0"

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.base_model_worker import app

    worker = AzureWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21001",
    )
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21001)

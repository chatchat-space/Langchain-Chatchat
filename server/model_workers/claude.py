import sys
from fastchat.conversation import Conversation
from server.model_workers.base import *
from server.utils import get_httpx_client
import json, httpx
from typing import List, Dict
from configs import logger, log_verbose


class ClaudeWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            controller_addr: str = None,
            worker_addr: str = None,
            model_name: str = "claude-3-opus-20240229",
            **kwargs,
    ):
        kwargs.update(model_name=model_name, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 1024)
        super().__init__(**kwargs)

    def create_claude_messages(self, messages) -> json:
        claude_msg = {"model": self.model_name, "max_tokens": self.context_len, "messages": []}

        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                continue
            claude_msg["messages"].append({"role": role, "content": content})

        return claude_msg

    def do_chat(self, params: ApiChatParams) -> Dict:
        data = self.create_claude_messages(messages=params.messages)
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': params.api_key,
            'anthropic-version': '2023-06-01'
        }
        if log_verbose:
            logger.info(f'{self.__class__.__name__}:url: {url}')
            logger.info(f'{self.__class__.__name__}:headers: {headers}')
            logger.info(f'{self.__class__.__name__}:data: {data}')

        text = ""
        json_string = ""
        timeout = httpx.Timeout(60.0)
        client = get_httpx_client(timeout=timeout)
        with client.post(url, headers=headers, json=data) as response:
            if response.status_code == 200:
                resp = response.json()
                if 'messages' in resp:
                    for message in resp['messages']:
                        if 'content' in message:
                            text += message['content']
                            yield {
                                "error_code": 0,
                                "text": text
                            }
            else:
                logger.error(f"Failed to get response: {response.text}")
                yield {
                    "error_code": response.status_code,
                    "text": "Failed to communicate with Claude API."
                }

    def get_embeddings(self, params):
        # Implement embedding retrieval if necessary
        pass

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        # Implement conversation template creation if necessary
        pass


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.base_model_worker import app

    worker = ClaudeWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21012",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21012)
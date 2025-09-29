import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import json
from pprint import pprint

from langchain import globals
from langchain.agents import AgentExecutor


from chatchat.server.utils import get_ChatOpenAI

# globals.set_debug(True)
# globals.set_verbose(True)

async def test_server_chat():
    from chatchat.server.chat.chat import chat

    mc = {
        "preprocess_model": {
            "qwen": {
                "temperature": 0.4,
                "max_tokens": 2048,
                "history_len": 100,
                "prompt_name": "default",
                "callbacks": False,
            }
        },
        "llm_model": {
            "qwen": {
                "temperature": 0.9,
                "max_tokens": 4096,
                "history_len": 3,
                "prompt_name": "default",
                "callbacks": True,
            }
        },
        "action_model": {
            "qwen": {
                "temperature": 0.01,
                "max_tokens": 4096,
                "prompt_name": "qwen",
                "callbacks": True,
            }
        },
        "postprocess_model": {
            "qwen": {
                "temperature": 0.01,
                "max_tokens": 4096,
                "prompt_name": "default",
                "callbacks": True,
            }
        },
    }

    tc = {"weather_check": {"use": False, "api-key": "your key"}}

    async for x in (
        await chat(
            "苏州天气如何",
            {},
            model_config=mc,
            tool_config=tc,
            conversation_id=None,
            history_len=-1,
            history=[],
            stream=True,
        )
    ).body_iterator:
        pprint(x)


async def test_text2image():
    from chatchat.server.chat.chat import chat

    mc = {
        "preprocess_model": {
            "qwen-api": {
                "temperature": 0.4,
                "max_tokens": 2048,
                "history_len": 100,
                "prompt_name": "default",
                "callbacks": False,
            }
        },
        "llm_model": {
            "qwen-api": {
                "temperature": 0.9,
                "max_tokens": 4096,
                "history_len": 3,
                "prompt_name": "default",
                "callbacks": True,
            }
        },
        "action_model": {
            "qwen-api": {
                "temperature": 0.01,
                "max_tokens": 4096,
                "prompt_name": "qwen",
                "callbacks": True,
            }
        },
        "postprocess_model": {
            "qwen-api": {
                "temperature": 0.01,
                "max_tokens": 4096,
                "prompt_name": "default",
                "callbacks": True,
            }
        },
        "image_model": {"sd-turbo": {}},
    }

    tc = {"text2images": {"use": True}}

    async for x in (
        await chat(
            "draw a house",
            {},
            model_config=mc,
            tool_config=tc,
            conversation_id=None,
            history_len=-1,
            history=[],
            stream=False,
        )
    ).body_iterator:
        x = json.loads(x)
        pprint(x)


asyncio.run(test1())

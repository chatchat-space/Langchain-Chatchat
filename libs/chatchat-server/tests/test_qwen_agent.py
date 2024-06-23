import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import json
from pprint import pprint

from langchain import globals
from langchain.agents import AgentExecutor

from chatchat.server.agent.agent_factory.qwen_agent import (
    create_structured_qwen_chat_agent,
)
from chatchat.server.agent.tools_factory.tools_registry import all_tools
from chatchat.server.callback_handler.agent_callback_handler import (
    AgentExecutorAsyncIteratorCallbackHandler,
)
from chatchat.server.utils import get_ChatOpenAI

# globals.set_debug(True)
# globals.set_verbose(True)


async def test1():
    callback = AgentExecutorAsyncIteratorCallbackHandler()
    qwen_model = get_ChatOpenAI("qwen", 0.01, streaming=False, callbacks=[callback])
    executor = create_structured_qwen_chat_agent(
        llm=qwen_model, tools=all_tools, callbacks=[callback]
    )
    # ret = executor.invoke({"input": "苏州今天冷吗"})
    ret = asyncio.create_task(executor.ainvoke({"input": "苏州今天冷吗"}))
    async for chunk in callback.aiter():
        print(chunk)
    # ret = executor.invoke("从知识库samples中查询chatchat项目简介")
    # ret = executor.invoke("chatchat项目主要issue有哪些")
    await ret


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

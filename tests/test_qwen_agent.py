import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from langchain.agents import AgentExecutor
from langchain_openai.chat_models import ChatOpenAI
# from langchain.chat_models.openai import ChatOpenAI
from server.utils import get_ChatOpenAI
from server.agent.tools_factory.tools_registry import all_tools
from server.agent.agent_factory.qwen_agent import create_structured_qwen_chat_agent
from server.callback_handler.agent_callback_handler import AgentExecutorAsyncIteratorCallbackHandler
from langchain import globals

globals.set_debug(True)
# globals.set_verbose(True)


async def main():
    callback = AgentExecutorAsyncIteratorCallbackHandler()
    tools = [t.copy(update={"callbacks": [callback]}) for t in all_tools]
    # qwen_model = get_ChatOpenAI("Qwen-1_8B-Chat", 0.01, streaming=True, callbacks=[callback])
    qwen_model = ChatOpenAI(base_url="http://127.0.0.1:9997/v1",
                            api_key="empty",
                            streaming=False,
                            temperature=0.01,
                            model="qwen",
                            callbacks=[callback],
                            )
    agent = create_structured_qwen_chat_agent(tools=tools, llm=qwen_model)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, callbacks=[callback])

    # ret = executor.invoke("苏州今天冷吗")
    ret = asyncio.create_task(executor.ainvoke({"input": "苏州今天冷吗"}))
    async for chunk in callback.aiter():
        print(chunk)
    # ret = executor.invoke("从知识库samples中查询chatchat项目简介")
    # ret = executor.invoke("chatchat项目主要issue有哪些")
    await ret

asyncio.run(main())

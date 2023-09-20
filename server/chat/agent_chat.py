from langchain.memory import ConversationBufferWindowMemory
from server.agent.tools import tools, tool_names
from server.agent.callbacks import CustomAsyncIteratorCallbackHandler, Status, dumps
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from server.agent.custom_template import CustomOutputParser, prompt
from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import LLM_MODEL, TEMPERATURE, HISTORY_LEN
from server.utils import wrap_done, get_ChatOpenAI
from langchain import LLMChain
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List
from server.chat.utils import History
import json


memory = ConversationBufferWindowMemory(k=HISTORY_LEN)
async def agent_chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                    history: List[History] = Body([],
                                                description="历史对话",
                                                examples=[[
                                                    {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                    {"role": "assistant", "content": "虎头虎脑"}]]
                                                ),
                    stream: bool = Body(False, description="流式输出"),
                    model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
                    temperature: float = Body(TEMPERATURE, description="LLM 采样温度", gt=0.0, le=1.0),
                    # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
                    ):
    history = [History.from_data(h) for h in history]

    async def chat_iterator() -> AsyncIterable[str]:
        callback = CustomAsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
        )
        output_parser = CustomOutputParser()
        llm_chain = LLMChain(llm=model, prompt=prompt)
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:"],
            allowed_tools=tool_names
        )
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                            tools=tools,
                                                            verbose=True,
                                                            memory=memory,
                                                            )
        # TODO: history is not used
        input_msg = History(role="user", content="{{ input }}").to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
        task = asyncio.create_task(wrap_done(
            agent_executor.acall(query, callbacks=[callback], include_run_info=True),
            callback.done),
        )
        if stream:
            async for chunk in callback.aiter():
                # Use server-sent-events to stream the response
                yield chunk
        else:
            result = []
            async for chunk in callback.aiter():
                data = json.loads(chunk)
                status = data["status"]
                if status == Status.start:
                    result.append(chunk)
                elif status == Status.running:
                    result[-1]["llm_output"] += chunk["llm_output"]
                elif status == Status.complete:
                    result[-1]["status"] = Status.complete
                elif status == Status.agent_finish:
                    result.append(chunk)
            yield dumps(result)

        await task

    return StreamingResponse(chat_iterator(),
                             media_type="text/event-stream")

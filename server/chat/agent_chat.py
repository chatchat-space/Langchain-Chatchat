from langchain.memory import ConversationBufferWindowMemory
from server.agent.tools import tools, tool_names
from server.agent.callbacks import CustomAsyncIteratorCallbackHandler, Status, dumps
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from server.agent.custom_template import CustomOutputParser, CustomPromptTemplate
from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import LLM_MODEL, TEMPERATURE, HISTORY_LEN
from server.utils import wrap_done, get_ChatOpenAI, get_prompt_template
from langchain.chains import LLMChain
from typing import AsyncIterable, Optional
import asyncio
from typing import List
from server.chat.utils import History
import json


async def agent_chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                     history: List[History] = Body([],
                                                   description="历史对话",
                                                   examples=[[
                                                       {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                                       {"role": "assistant", "content": "虎头虎脑"}]]
                                                   ),
                     stream: bool = Body(False, description="流式输出"),
                     model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
                     temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                     prompt_name: str = Body("agent_chat",
                                             description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                     # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
                     ):
    history = [History.from_data(h) for h in history]

    async def agent_chat_iterator(
            query: str,
            history: Optional[List[History]],
            model_name: str = LLM_MODEL,
            prompt_name: str = prompt_name,
    ) -> AsyncIterable[str]:
        callback = CustomAsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
        )

        prompt_template = CustomPromptTemplate(
            template=get_prompt_template(prompt_name),
            tools=tools,
            input_variables=["input", "intermediate_steps", "history"]
        )
        output_parser = CustomOutputParser()
        llm_chain = LLMChain(llm=model, prompt=prompt_template)
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["Observation:", "Observation:\n", "<|im_end|>"], # Qwen模型中使用这个
            # stop=["Observation:", "Observation:\n"], # 其他模型，注意模板
            allowed_tools=tool_names,
        )
        # 把history转成agent的memory
        memory = ConversationBufferWindowMemory(k=HISTORY_LEN * 2)

        for message in history:
            # 检查消息的角色
            if message.role == 'user':
                # 添加用户消息
                memory.chat_memory.add_user_message(message.content)
            else:
                # 添加AI消息
                memory.chat_memory.add_ai_message(message.content)
        agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                            tools=tools,
                                                            verbose=True,
                                                            memory=memory,
                                                            )
        input_msg = History(role="user", content="{{ input }}").to_msg_template(False)
        task = asyncio.create_task(wrap_done(
            agent_executor.acall(query, callbacks=[callback], include_run_info=True),
            callback.done),
        )
        if stream:
            async for chunk in callback.aiter():
                tools_use = []
                # Use server-sent-events to stream the response
                data = json.loads(chunk)
                if data["status"] == Status.error:
                    tools_use.append("工具调用失败:\n" + data["error"])
                    yield json.dumps({"tools": tools_use}, ensure_ascii=False)
                    yield json.dumps({"answer": "(工具调用失败，请查看工具栏报错) \n\n"}, ensure_ascii=False)
                if data["status"] == Status.start or data["status"] == Status.complete:
                    continue
                if data["status"] == Status.agent_action:
                    yield json.dumps({"answer": "(正在使用工具，请注意工具栏变化) \n\n"}, ensure_ascii=False)
                if data["status"] == Status.agent_finish:
                    tools_use.append("工具名称: " + data["tool_name"])
                    tools_use.append("工具输入: " + data["input_str"])
                    tools_use.append("工具输出: " + data["output_str"])
                    yield json.dumps({"tools": tools_use}, ensure_ascii=False)
                yield json.dumps({"answer": data["llm_token"]}, ensure_ascii=False)

        else:
            pass
            # agent必须要steram=True,这部分暂时没有完成
            # result = []
            # async for chunk in callback.aiter():
            #     data = json.loads(chunk)
            #     status = data["status"]
            #     if status == Status.start:
            #         result.append(chunk)
            #     elif status == Status.running:
            #         result[-1]["llm_token"] += chunk["llm_token"]
            #     elif status == Status.complete:
            #         result[-1]["status"] = Status.complete
            #     elif status == Status.agent_finish:
            #         result.append(chunk)
            #     elif status == Status.agent_finish:
            #         pass
            # yield dumps(result)

        await task

    return StreamingResponse(agent_chat_iterator(query=query,
                                                 history=history,
                                                 model_name=model_name,
                                                 prompt_name=prompt_name),
                             media_type="text/event-stream")

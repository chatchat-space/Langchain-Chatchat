from langchain.memory import ConversationBufferWindowMemory
from server.agent.tools_select import tools, tool_names
from server.agent.callbacks import CustomAsyncIteratorCallbackHandler, Status
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from server.agent.custom_template import CustomOutputParser, CustomPromptTemplate
from fastapi import Body
from fastapi.responses import StreamingResponse
from configs import LLM_MODEL, TEMPERATURE, HISTORY_LEN
from server.utils import wrap_done, get_ChatOpenAI, get_prompt_template
from langchain.chains import LLMChain
from typing import AsyncIterable, Optional, Dict
import asyncio
from typing import List
from server.chat.utils import History
import json
from server.agent import model_container
from server.knowledge_base.kb_service.base import get_kb_details

async def agent_chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                     history: List[History] = Body([],
                                                   description="历史对话",
                                                   examples=[[
                                                       {"role": "user", "content": "请使用知识库工具查询今天北京天气"},
                                                       {"role": "assistant", "content": "使用天气查询工具查询到今天北京多云，10-14摄氏度，东北风2级，易感冒"}]]
                                                   ),
                     stream: bool = Body(False, description="流式输出"),
                     model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
                     temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                     max_tokens: int = Body(None, description="限制LLM生成Token数量，默认None代表模型最大值"),
                     prompt_name: str = Body("default",description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
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
            max_tokens=max_tokens,
            callbacks=[callback],
        )

        ## 传入全局变量来实现agent调用
        kb_list = {x["kb_name"]: x for x in get_kb_details()}
        model_container.DATABASE = {name: details['kb_info'] for name, details in kb_list.items()}
        model_container.MODEL = model

        prompt_template = get_prompt_template("agent_chat", prompt_name)
        prompt_template_agent = CustomPromptTemplate(
            template=prompt_template,
            tools=tools,
            input_variables=["input", "intermediate_steps", "history"]
        )
        output_parser = CustomOutputParser()
        llm_chain = LLMChain(llm=model, prompt=prompt_template_agent)
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:", "Observation:", "<|im_end|>"],  # Qwen模型中使用这个
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
        while True:
            try:
                task = asyncio.create_task(wrap_done(
                    agent_executor.acall(query, callbacks=[callback], include_run_info=True),
                    callback.done))
                break
            except:
                pass

        if stream:
            async for chunk in callback.aiter():
                tools_use = []
                # Use server-sent-events to stream the response
                data = json.loads(chunk)
                if data["status"] == Status.start or data["status"] == Status.complete:
                    continue
                elif data["status"] == Status.error:
                    tools_use.append("\n```\n")
                    tools_use.append("工具名称: " + data["tool_name"])
                    tools_use.append("工具状态: " + "调用失败")
                    tools_use.append("错误信息: " + data["error"])
                    tools_use.append("重新开始尝试")
                    tools_use.append("\n```\n")
                    yield json.dumps({"tools": tools_use}, ensure_ascii=False)
                elif data["status"] == Status.tool_finish:
                    tools_use.append("\n```\n")
                    tools_use.append("工具名称: " + data["tool_name"])
                    tools_use.append("工具状态: " + "调用成功")
                    tools_use.append("工具输入: " + data["input_str"])
                    tools_use.append("工具输出: " + data["output_str"])
                    tools_use.append("\n```\n")
                    yield json.dumps({"tools": tools_use}, ensure_ascii=False)
                elif data["status"] == Status.agent_finish:
                    yield json.dumps({"final_answer": data["final_answer"]}, ensure_ascii=False)
                else:
                    yield json.dumps({"answer": data["llm_token"]}, ensure_ascii=False)


        else:
            answer = ""
            final_answer = ""
            async for chunk in callback.aiter():
                # Use server-sent-events to stream the response
                data = json.loads(chunk)
                if data["status"] == Status.start or data["status"] == Status.complete:
                    continue
                if data["status"] == Status.error:
                    answer += "\n```\n"
                    answer += "工具名称: " + data["tool_name"] + "\n"
                    answer += "工具状态: " + "调用失败" + "\n"
                    answer += "错误信息: " + data["error"] + "\n"
                    answer += "\n```\n"
                if data["status"] == Status.tool_finish:
                    answer += "\n```\n"
                    answer += "工具名称: " + data["tool_name"] + "\n"
                    answer += "工具状态: " + "调用成功" + "\n"
                    answer += "工具输入: " + data["input_str"] + "\n"
                    answer += "工具输出: " + data["output_str"] + "\n"
                    answer += "\n```\n"
                if data["status"] == Status.agent_finish:
                    final_answer = data["final_answer"]
                else:
                    answer += data["llm_token"]

            yield json.dumps({"answer": answer, "final_answer": final_answer}, ensure_ascii=False)
        await task

    return StreamingResponse(agent_chat_iterator(query=query,
                                                 history=history,
                                                 model_name=model_name,
                                                 prompt_name=prompt_name),
                             media_type="text/event-stream")

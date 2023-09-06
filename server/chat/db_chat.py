from fastapi import Body
from fastapi.responses import StreamingResponse
from configs.model_config import llm_model_dict, LLM_MODEL, DB_PROMPT_TEMPLATE, SQL_PROMPT_TEMPLATE
from server.chat.utils import wrap_done
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List
from server.chat.utils import History
from server.sql_db.util import get_table_info, execute_sql_query, extract_first_select
import json


def db_chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
            db_type: str = Body(..., description="数据库类型"),
            host: str = Body(..., description="数据库地址"),
            username: str = Body(..., description="用户名"),
            password: str = Body(..., description="密码"),
            database: str = Body(..., description="数据库"),
            schema: str = Body(..., description="模式"),
            history: List[History] = Body([],
                                          description="历史对话",
                                          examples=[[
                                              {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                              {"role": "assistant", "content": "虎头虎脑"}]]
                                          ),
            stream: bool = Body(False, description="流式输出"),
            model_name: str = Body(LLM_MODEL, description="LLM 模型名称。"),
            ):
    history = [History.from_data(h) for h in history]

    async def chat_iterator(query: str,
                            db_type: str,
                            host: str,
                            username: str,
                            password: str,
                            database: str,
                            schema: str,
                            history: List[History] = [],
                            model_name: str = LLM_MODEL,
                            ) -> AsyncIterable[str]:

        callback = AsyncIteratorCallbackHandler()

        model = ChatOpenAI(
            streaming=True,
            verbose=True,
            callbacks=[callback],
            openai_api_key=llm_model_dict[model_name]["api_key"],
            openai_api_base=llm_model_dict[model_name]["api_base_url"],
            model_name=model_name,
            openai_proxy=llm_model_dict[model_name].get("openai_proxy")
        )

        input_msg = History(role="user", content=DB_PROMPT_TEMPLATE).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
        chain = LLMChain(prompt=chat_prompt, llm=model)

        # 获取表信息
        table_schemas = get_table_info(db_type, host, username, password, database, schema)
        print(table_schemas)
        # 根据表信息，使用模型生成sql描述
        sql = chain.run({"tableSchemas": table_schemas, "dataSourceType": db_type, "question": query})
        # 获取sql语句
        selected_part = extract_first_select(sql)
        print(selected_part)

        # 查询数据库信息
        source_db = []
        if selected_part is None:
            sql_query_results = "查询结果失败"
            source_db.append(sql_query_results)
        else:
            sql_query_results = execute_sql_query(db_type, host, username, password, database, selected_part, schema)
            # 查询结果格式化
            for doc in sql_query_results:
                text = f"""\n\n{doc}\n\n"""
                source_db.append(text)
            print(sql_query_results)

        # Begin a task that runs in the background.
        input_msg_sql = History(role="user", content=SQL_PROMPT_TEMPLATE).to_msg_template(False)
        chat_prompt_sql = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg_sql])
        chain_sql = LLMChain(prompt=chat_prompt_sql, llm=model)
        task = asyncio.create_task(wrap_done(
            chain_sql.acall({"question": query, "queryResults": sql_query_results}),
            callback.done),
        )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield json.dumps({"answer": token,
                                  "sql": sql,
                                  "docs": source_db},
                                 ensure_ascii=False)
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield json.dumps({"answer": answer,
                              "sql": sql,
                              "docs": source_db},
                             ensure_ascii=False)

        await task

    return StreamingResponse(
        chat_iterator(query, db_type, host, username, password, database, schema, history, model_name),
        media_type="text/event-stream")

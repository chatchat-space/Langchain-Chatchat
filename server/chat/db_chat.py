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
from server.mysql_db.mysql_util import get_table_info, execute_sql_query
import json

def db_chat(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
              type: str = Body(..., description="数据库类型"),
              host: str = Body(..., description="数据库地址"),
              username: str = Body(..., description="用户名"),
              password: str = Body(..., description="密码"),
              database: str = Body(..., description="数据库"),
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
                            type: str,
                            host: str,
                            username: str,
                            password: str,
                            database: str,
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

        table_schemas = get_table_info(type, host, username, password, database)
        print(table_schemas)
        sql = chain.run({"tableSchemas": table_schemas, "dataSourceType": type, "question": query})
        print(sql)
        start_index = sql.find('SELECT')  # 查找 SELECT 的起始位置
        end_index = sql.find(';') + 1  # 查找 ; 的结束位置，并添加 1 以包括 ;
        # 提取子字符串
        selected_part = sql[start_index:end_index]
        sql_query_results = execute_sql_query(type, host, username, password, database, selected_part)
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
        source_db = []
        for doc in sql_query_results:
            text = f"""\n\n{doc}\n\n"""
            source_db.append(text)
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

    return StreamingResponse(chat_iterator(query, type, host, username, password, database, history, model_name),
                             media_type="text/event-stream")

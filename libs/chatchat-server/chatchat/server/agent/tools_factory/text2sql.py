from langchain.chains import LLMChain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts.prompt import PromptTemplate
from langchain_experimental.sql import SQLDatabaseChain, SQLDatabaseSequentialChain
from sqlalchemy import event
from sqlalchemy.exc import OperationalError

from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

from .tools_registry import BaseToolOutput, regist_tool

READ_ONLY_PROMPT_TEMPLATE = """You are a MySQL expert. The database is currently in read-only mode. 
Given an input question, determine if the related SQL can be executed in read-only mode.
If the SQL can be executed normally, return Answer:'SQL can be executed normally'.
If the SQL cannot be executed normally, return Answer: 'SQL cannot be executed normally'.
Use the following format:

Answer: Final answer here

Question: {query}
"""


# 定义一个拦截器函数来检查SQL语句，以支持read-only,可修改下面的write_operations，以匹配你使用的数据库写操作关键字
def intercept_sql(conn, cursor, statement, parameters, context, executemany):
    # List of SQL keywords that indicate a write operation
    write_operations = (
        "insert",
        "update",
        "delete",
        "create",
        "drop",
        "alter",
        "truncate",
        "rename",
    )
    # Check if the statement starts with any of the write operation keywords
    if any(statement.strip().lower().startswith(op) for op in write_operations):
        raise OperationalError(
            "Database is read-only. Write operations are not allowed.",
            params=None,
            orig=None,
        )


def query_database(query: str, config: dict):
    model_name= config["model_name"]
    top_k = config["top_k"]
    return_intermediate_steps = config["return_intermediate_steps"]
    sqlalchemy_connect_str = config["sqlalchemy_connect_str"]
    read_only = config["read_only"]
    db = SQLDatabase.from_uri(sqlalchemy_connect_str)

    from chatchat.server.utils import get_ChatOpenAI

    llm = get_ChatOpenAI(
        model_name=model_name,
        temperature=0.1,
        streaming=True,
        local_wrap=True,
        verbose=True,
    )
    table_names = config["table_names"]
    table_comments = config["table_comments"]
    result = None

    # 如果发现大模型判断用什么表出现问题，尝试给langchain提供额外的表说明，辅助大模型更好的判断应该使用哪些表，尤其是SQLDatabaseSequentialChain模式下,是根据表名做的预测，很容易误判
    # 由于langchain固定了输入参数，所以只能通过query传递额外的表说明
    if table_comments:
        TABLE_COMMNET_PROMPT = (
            "\n\nI will provide some special notes for a few tables:\n\n"
        )
        table_comments_str = "\n".join([f"{k}:{v}" for k, v in table_comments.items()])
        query = query + TABLE_COMMNET_PROMPT + table_comments_str + "\n\n"

    if read_only:
        # 在read_only下，先让大模型判断只读模式是否能满足需求，避免后续执行过程报错，返回友好提示。
        READ_ONLY_PROMPT = PromptTemplate(
            input_variables=["query"],
            template=READ_ONLY_PROMPT_TEMPLATE,
        )
        read_only_chain = LLMChain(
            prompt=READ_ONLY_PROMPT,
            llm=llm,
        )
        read_only_result = read_only_chain.invoke(query)
        if "SQL cannot be executed normally" in read_only_result["text"]:
            return "当前数据库为只读状态，无法满足您的需求！"

        # 当然大模型不能保证完全判断准确，为防止大模型判断有误，再从拦截器层面拒绝写操作
        event.listen(db._engine, "before_cursor_execute", intercept_sql)

    # 如果不指定table_names，优先走SQLDatabaseSequentialChain，这个链会先预测需要哪些表，然后再将相关表输入SQLDatabaseChain
    # 这是因为如果不指定table_names，直接走SQLDatabaseChain，Langchain会将全量表结构传递给大模型，可能会因token太长从而引发错误，也浪费资源
    # 如果指定了table_names，直接走SQLDatabaseChain，将特定表结构传递给大模型进行判断
    if len(table_names) > 0:
        db_chain = SQLDatabaseChain.from_llm(
            llm,
            db,
            verbose=True,
            top_k=top_k,
            return_intermediate_steps=return_intermediate_steps,
        )
        result = db_chain.invoke({"query": query, "table_names_to_use": table_names})
    else:
        # 先预测会使用哪些表，然后再将问题和预测的表给大模型
        db_chain = SQLDatabaseSequentialChain.from_llm(
            llm,
            db,
            verbose=True,
            top_k=top_k,
            return_intermediate_steps=return_intermediate_steps,
        )
        result = db_chain.invoke(query)

    context = f"""查询结果:{result['result']}\n\n"""

    intermediate_steps = result["intermediate_steps"]
    # 如果存在intermediate_steps，且这个数组的长度大于2，则保留最后两个元素，因为前面几个步骤存在示例数据，容易引起误解
    if intermediate_steps:
        if len(intermediate_steps) > 2:
            sql_detail = intermediate_steps[-2:-1][0]["input"]
            # sql_detail截取从SQLQuery到Answer:之间的内容
            sql_detail = sql_detail[
                sql_detail.find("SQLQuery:") + 9 : sql_detail.find("Answer:")
            ]
            context = context + "执行的sql:'" + sql_detail + "'\n\n"
    return context


@regist_tool(title="数据库对话")
def text2sql(
    query: str = Field(
        description="No need for SQL statements,just input the natural language that you want to chat with database"
    ),
):
    """Use this tool to chat with  database,Input natural language, then it will convert it into SQL and execute it in the database, then return the execution result."""
    tool_config = get_tool_config("text2sql")
    return BaseToolOutput(query_database(query=query, config=tool_config))

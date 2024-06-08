from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain,SQLDatabaseSequentialChain
from chatchat.server.utils import get_tool_config
from chatchat.server.pydantic_v1 import Field
from .tools_registry import regist_tool, BaseToolOutput

def query_database(query: str,
                  config: dict):
    db_user = config["db_user"]
    db_password = config["db_password"]
    db_host = config["db_host"]
    db_name = config["db_name"]
    top_k = config["top_k"]
    return_intermediate_steps = config["return_intermediate_steps"]
    db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
    from chatchat.server.api_server.chat_routes import global_model_name
    from chatchat.server.utils import  get_ChatOpenAI
    llm = get_ChatOpenAI(
                model_name=global_model_name,
                temperature=0,
                streaming=True,
                local_wrap=True,
                verbose=True
            )
    table_names=config["table_names"]
    table_comments=config["table_comments"]
    result = None

    #如果发现大模型判断用什么表出现问题，尝试给langchain提供额外的表说明，辅助大模型更好的判断应该使用哪些表，尤其是SQLDatabaseSequentialChain模式下,是根据表名做的预测，很容易误判
    #由于langchain固定了输入参数，所以只能通过query传递额外的表说明
    if table_comments:
            TABLE_COMMNET_PROMPT="\n\nI will provide some special notes for a few tables:\n\n"
            table_comments_str="\n".join([f"{k}:{v}" for k,v in table_comments.items()])
            query=query+TABLE_COMMNET_PROMPT+table_comments_str+"\n\n"

    #如果不指定table_names，优先走SQLDatabaseSequentialChain，这个链会先预测需要哪些表，然后再将相关表输入SQLDatabaseChain
    #这是因为如果不指定table_names，直接走SQLDatabaseChain，Langchain会将全量表结构传递给大模型，可能会因token太长从而引发错误，也浪费资源
    #如果指定了table_names，直接走SQLDatabaseChain，将特定表结构传递给大模型进行判断
    if len(table_names) > 0:
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True,top_k=top_k,return_intermediate_steps=return_intermediate_steps)
        result = db_chain.invoke({"query":query,"table_names_to_use":table_names})
    else:
        #先预测会使用哪些表，然后再将问题和预测的表给大模型
        db_chain = SQLDatabaseSequentialChain.from_llm(llm, db, verbose=True,top_k=top_k,return_intermediate_steps=return_intermediate_steps)
        result = db_chain.invoke(query)
    
    context = f"""查询结果:{result['result']}\n\n"""

    intermediate_steps=result["intermediate_steps"]
    #如果存在intermediate_steps，且这个数组的长度大于2，则保留最后两个元素，因为前面几个步骤存在示例数据，容易引起误解
    if intermediate_steps:
        if len(intermediate_steps)>2:
            sql_detail=intermediate_steps[-2:-1][0]["input"]
            # sql_detail截取从SQLQuery到Answer:之间的内容
            sql_detail=sql_detail[sql_detail.find("SQLQuery:")+9:sql_detail.find("Answer:")]
            context = context+"执行的sql:'"+sql_detail+"'\n\n"
    return context
    

@regist_tool(title="Text2Sql")
def text2sql(query: str = Field(description="No need for SQL statements,just input the natural language that you want to chat with database")):
    '''Use this tool to chat with  database,Input natural language, then it will convert it into SQL and execute it in the database, then return the execution result.'''
    tool_config = get_tool_config("text2sql")
    return BaseToolOutput(query_database(query=query, config=tool_config))

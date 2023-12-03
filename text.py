from langchain.tools import ShellTool

shell_tool = ShellTool()

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
import os
from langchain.schema.runnable import RunnableBranch
from langchain.agents import AgentType, Tool, initialize_agent

# 把这三个加入环境变量
# "model_name": "gpt-4-1106-preview",
# "api_key": "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",
os.environ["OPENAI_API_KEY"] = "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"

chain = (
        PromptTemplate.from_template(
            """
            请你根据我的描述，认为是否需要使用工具，还是可以直接回答问题。你只要回答一个数字,1 或者 0，1代表需要使用工具，0代表不需要使用工具。\n
            以下几种情况要使用工具,请返回数字1\n
            1. 实时性的问题，例如天气，日期，地点等信息\n
            2. 需要数学计算的问题\n
            3. 需要查询数据，地点等精确数据\n
            4. 需要行业知识的问题\n
            <question>
            {input}
            </question>
            结论:"""
        )
        | ChatOpenAI()
        | StrOutputParser()
)
llm_chain = (
        PromptTemplate.from_template(
            """你是一个聪明的助手，请根据我的描述回答。
            Question: {input}
            Answer:"""
        )
        | ChatOpenAI()
)
tool_chain = (
        PromptTemplate.from_template(
            """ 无论我输入什么，你只能使用'喵喵喵'来回答
            Question: {input}
            Answer:"""
        )
        | ChatOpenAI()
)

shell_tool.description = shell_tool.description + f"args {shell_tool.args}".replace(
    "{", "{{"
).replace("}", "}}")
agent = initialize_agent(tools=[shell_tool], agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, llm=ChatOpenAI())

branch = RunnableBranch(
    (lambda x: "1" in x["topic"].lower(), agent),
    llm_chain
)

full_chain = {"topic": chain, "input": lambda x: x["input"]} | branch
ans = full_chain.invoke({"input": "当前文件夹是"})
print(ans)

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
import asyncio
from argparse import Namespace
from models.loader.args import parser
from models.loader import LoaderCheckPoint


import models.shared as shared

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import PromptTemplate
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from typing import List, Set



class CustomLLMSingleActionAgent(ZeroShotAgent):
    allowed_tools: List[str]

    def __init__(self, *args, **kwargs):
        super(CustomLLMSingleActionAgent, self).__init__(*args, **kwargs)
        self.allowed_tools = kwargs['allowed_tools']

    def get_allowed_tools(self) -> Set[str]:
        return set(self.allowed_tools)


async def dispatch(args: Namespace):
    args_dict = vars(args)

    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()

    template = """This is a conversation between a human and a bot:
    
{chat_history}

Write a summary of the conversation for {input}:
"""

    prompt = PromptTemplate(
        input_variables=["input", "chat_history"],
        template=template
    )
    memory = ConversationBufferMemory(memory_key="chat_history")
    readonlymemory = ReadOnlySharedMemory(memory=memory)
    summry_chain = LLMChain(
        llm=llm_model_ins,
        prompt=prompt,
        verbose=True,
        memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
    )


    tools = [
        Tool(
            name="Summary",
            func=summry_chain.run,
            description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary."
        )
    ]

    prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
    suffix = """Begin!
     
Question: {input}
{agent_scratchpad}"""


    prompt = CustomLLMSingleActionAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input",   "agent_scratchpad"]
    )
    tool_names = [tool.name for tool in tools]
    llm_chain = LLMChain(llm=llm_model_ins, prompt=prompt)
    agent = CustomLLMSingleActionAgent(llm_chain=llm_chain, tools=tools, allowed_tools=tool_names)
    agent_chain = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools)

    agent_chain.run(input="你好")
    agent_chain.run(input="你是谁?")
    agent_chain.run(input="我们之前聊了什么?")

if __name__ == '__main__':
    args = None
    args = parser.parse_args(args=['--model-dir', '/media/checkpoint/',  '--model', 'vicuna-13b-hf', '--no-remote-model', '--load-in-8bit'])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dispatch(args))

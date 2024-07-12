from typing import List, Sequence

from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

from chatchat.server.agent.agent_factory import create_structured_qwen_chat_agent
from chatchat.server.agent.agent_factory.glm3_agent import (
    create_structured_glm3_chat_agent,
)


def agents_registry(
        llm: BaseLanguageModel,
        tools: Sequence[BaseTool] = [],
        callbacks: List[BaseCallbackHandler] = [],
        prompt: str = None,
        verbose: bool = False,
):
    # llm.callbacks = callbacks
    llm.streaming = False  # qwen agent not support streaming

    # Write any optimized method here.
    if "glm3" in llm.model_name.lower():
        # An optimized method of langchain Agent that uses the glm3 series model
        agent = create_structured_glm3_chat_agent(llm=llm, tools=tools)

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=verbose, callbacks=callbacks
        )

        return agent_executor
    elif "qwen" in llm.model_name.lower():
        return create_structured_qwen_chat_agent(
            llm=llm, tools=tools, callbacks=callbacks
        )
    else:
        if prompt is not None:
            prompt = ChatPromptTemplate.from_messages([SystemMessage(content=prompt)])
        else:
            prompt = hub.pull("hwchase17/structured-chat-agent")  # default prompt
        agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=verbose, callbacks=callbacks
        )

        return agent_executor

# -*- coding: utf-8 -*-
import asyncio
import sys
from contextlib import AsyncExitStack

from langchain.agents.agent import RunnableMultiActionAgent
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from chatchat.server.utils import get_prompt_template_dict
from langchain_chatchat.agents.all_tools_agent import PlatformToolsAgentExecutor
from langchain_chatchat.agents.react.create_prompt_template import create_prompt_glm3_template, \
    create_prompt_structured_react_template, create_prompt_platform_template, create_prompt_gpt_tool_template, \
    create_prompt_platform_knowledge_mode_template
from langchain_chatchat.agents.structured_chat.glm3_agent import (
    create_structured_glm3_chat_agent,
)
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union, cast,
)

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent, create_tool_calling_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langchain_chatchat.agent_toolkits.mcp_kit.tools import MCPStructuredTool

from langchain_chatchat.agents.structured_chat.platform_knowledge_bind import create_platform_knowledge_agent
from langchain_chatchat.agents.structured_chat.platform_tools_bind import create_platform_tools_agent
from langchain_chatchat.agents.structured_chat.qwen_agent import create_qwen_chat_agent
from langchain_chatchat.agents.structured_chat.structured_chat_agent import create_chat_agent


def agents_registry(
        agent_type: str,
        llm: BaseLanguageModel,
        llm_with_platform_tools: List[Dict[str, Any]] = [],
        tools: Sequence[Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]] = [],
        mcp_tools: Sequence[MCPStructuredTool] = [],
        callbacks: List[BaseCallbackHandler] = [],
        verbose: bool = False,
        **kwargs: Any,
):
    # Write any optimized method here.
    # TODO agent params of PlatformToolsAgentExecutor or AgentExecutor  enable return_intermediate_steps=True,
    if "glm3" == agent_type:
        # An optimized method of langchain Agent that uses the glm3 series model
        template = get_prompt_template_dict("action_model", agent_type)
        prompt = create_prompt_glm3_template(agent_type, template=template)
        agent = create_structured_glm3_chat_agent(llm=llm,
                                                  tools=tools,
                                                  prompt=prompt,
                                                  llm_with_platform_tools=llm_with_platform_tools
                                                  )

        agent_executor = PlatformToolsAgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            callbacks=callbacks,
            return_intermediate_steps=True,
        )
        return agent_executor
    elif "qwen" == agent_type:
        llm.streaming = False  # qwen agent not support streaming

        template = get_prompt_template_dict("action_model", agent_type)
        prompt = create_prompt_structured_react_template(agent_type, template=template)
        agent = create_qwen_chat_agent(llm=llm,
                                       tools=tools,
                                       prompt=prompt,
                                       llm_with_platform_tools=llm_with_platform_tools)

        agent_executor = PlatformToolsAgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            callbacks=callbacks,
            return_intermediate_steps=True,
        )
        return agent_executor
    elif "platform-agent" == agent_type:

        template = get_prompt_template_dict("action_model", agent_type)
        prompt = create_prompt_platform_template(agent_type, template=template)
        agent = create_platform_tools_agent(llm=llm,
                                            tools=tools,
                                            prompt=prompt,
                                            llm_with_platform_tools=llm_with_platform_tools)

        agent_executor = PlatformToolsAgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            callbacks=callbacks,
            return_intermediate_steps=True,
        )
        return agent_executor
    elif agent_type == 'structured-chat-agent':

        template = get_prompt_template_dict("action_model", agent_type)
        prompt = create_prompt_structured_react_template(agent_type, template=template)
        agent = create_chat_agent(llm=llm,
                                  tools=tools,
                                  prompt=prompt,
                                  llm_with_platform_tools=llm_with_platform_tools
                                  )

        agent_executor = PlatformToolsAgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            callbacks=callbacks,
            return_intermediate_steps=True,
        )
        return agent_executor
    elif agent_type == 'default':
        # this agent single chat
        template = get_prompt_template_dict("action_model", "default")
        prompt = ChatPromptTemplate.from_messages([SystemMessage(content=template.get("SYSTEM_PROMPT"))])

        agent = create_chat_agent(llm=llm,
                                  tools=tools,
                                  prompt=prompt,
                                  llm_with_platform_tools=llm_with_platform_tools
                                  )

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=verbose, callbacks=callbacks,
            return_intermediate_steps=True,
            **kwargs,
        )

        return agent_executor

    elif agent_type == "openai-functions":
        # agent only tools agent_scratchpad chat ,this runnable supper history message
        template = get_prompt_template_dict("action_model", agent_type)
        prompt = create_prompt_gpt_tool_template(agent_type, template=template)

        # prompt pre partial "tool_names" var
        prompt = prompt.partial(
            tool_names=", ".join([t.name for t in tools]),
        )
        runnable = create_openai_tools_agent(llm, tools, prompt)
        agent = RunnableMultiActionAgent(
            runnable=runnable,
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs,
        )
        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=verbose, callbacks=callbacks,

            return_intermediate_steps=True,
            **kwargs,
        )
        return agent_executor
    elif agent_type in ("openai-tools", "tool-calling"):
        # agent only tools agent_scratchpad chat ,this runnable not history message
        function_prefix = kwargs.get("FUNCTIONS_PREFIX")
        function_suffix = kwargs.get("FUNCTIONS_SUFFIX")
        messages = [
            SystemMessage(content=cast(str, function_prefix)),
            HumanMessagePromptTemplate.from_template("{input}"),
            AIMessage(content=function_suffix),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        prompt = ChatPromptTemplate.from_messages(messages)
        if agent_type == "openai-tools":
            runnable = create_openai_tools_agent(llm, tools, prompt)
        else:
            runnable = create_tool_calling_agent(llm, tools, prompt)
        agent = RunnableMultiActionAgent(
            runnable=runnable,
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs,
        )
        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=verbose, callbacks=callbacks,
            return_intermediate_steps=True,
            **kwargs,
        )
        return agent_executor

    elif "platform-knowledge-mode" == agent_type:
  
        template = get_prompt_template_dict("action_model", agent_type)
        prompt = create_prompt_platform_knowledge_mode_template(agent_type, template=template)
        agent = create_platform_knowledge_agent(llm=llm,
                                                current_working_directory=kwargs.get("current_working_directory", "/tmp"),
                                                tools=tools,
                                                mcp_tools=mcp_tools,
                                                llm_with_platform_tools=llm_with_platform_tools,
                                                prompt=prompt)

        agent_executor = PlatformToolsAgentExecutor(
            agent=agent,
            tools=tools,
            mcp_tools=mcp_tools,
            verbose=verbose,
            callbacks=callbacks,
            return_intermediate_steps=True,
        )
        return agent_executor

    else:
        raise ValueError(
            f"Agent type {agent_type} not supported at the moment. Must be one of "
            "'tool-calling', 'openai-tools', 'openai-functions', "
            "'default','ChatGLM3','structured-chat-agent','platform-agent','qwen','glm3'"
        )


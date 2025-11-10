# -*- coding: utf-8 -*-
import asyncio
import json
import logging
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
    Union,
)
import os
import sys
from langchain import hub
from langchain.agents import AgentExecutor
from langchain_core.agents import AgentAction
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import convert_to_messages
from langchain_core.runnables import RunnableConfig, RunnableSerializable
from langchain_core.runnables.base import RunnableBindingBase
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI
from openai import BaseModel
from pydantic import ConfigDict
from typing_extensions import ClassVar

from langchain_chatchat.agent_toolkits.all_tools.registry import (
    TOOL_STRUCT_TYPE_TO_TOOL_CLASS,
)
from langchain_chatchat.agent_toolkits.all_tools.struct_type import (
    AdapterAllToolStructType,
)
from langchain_chatchat.agent_toolkits.all_tools.tool import (
    AdapterAllTool,
    BaseToolOutput,
)
from langchain_chatchat.agents.all_tools_agent import PlatformToolsAgentExecutor
from langchain_chatchat.agents.format_scratchpad.all_tools import (
    format_to_platform_tool_messages,
)
from langchain_chatchat.agents.output_parsers import PlatformToolsAgentOutputParser
from langchain_chatchat.agents.platform_tools.schema import (
    PlatformToolsAction,
    PlatformToolsActionToolEnd,
    PlatformToolsActionToolStart,
    PlatformToolsFinish,
    PlatformToolsLLMStatus, PlatformToolsApprove,
)
from langchain_chatchat.callbacks.agent_callback_handler import (
    AgentExecutorAsyncIteratorCallbackHandler,
    AgentStatus,
)
from langchain_chatchat.agent_toolkits.mcp_kit.client import MultiServerMCPClient, StdioConnection, SSEConnection
from langchain_chatchat.chat_models import ChatPlatformAI
from langchain_chatchat.chat_models.base import ChatPlatformAI
from langchain_chatchat.utils import History
from langchain_chatchat.utils.__init__ import PYDANTIC_V2

logger = logging.getLogger()


def _is_assistants_builtin_tool(
        tool: Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool],
) -> bool:
    """platform tools built-in"""
    assistants_builtin_tools = AdapterAllToolStructType.__members__.values()
    return (
            isinstance(tool, dict)
            and ("type" in tool)
            and (tool["type"] in assistants_builtin_tools)
    )


def _get_assistants_tool(
        tool: Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool],
) -> Dict[str, Any]:
    """Convert a raw function/class to an ZhipuAI tool."""
    if _is_assistants_builtin_tool(tool):
        return tool  # type: ignore
    else:
        # in case of a custom tool, convert it to an function of type
        return convert_to_openai_tool(tool)


async def wrap_done(fn: Awaitable, event: asyncio.Event):
    """Wrap an awaitable with a event to signal when it's done or an exception is raised."""
    try:
        await fn
    except Exception as e:
        msg = f"Caught exception: {e}"
        logger.error(f"{e.__class__.__name__}: {msg}", exc_info=e)
    finally:
        # Signal the aiter to stop.
        event.set()


OutputType = Union[
    PlatformToolsAction,
    PlatformToolsActionToolStart,
    PlatformToolsActionToolEnd,
    PlatformToolsFinish,
    PlatformToolsLLMStatus,
]


class PlatformToolsRunnable(RunnableSerializable[Dict, OutputType]):
    agent_executor: AgentExecutor
    """Platform AgentExecutor."""
    agent_type: str
    """agent_type."""

    """工具模型"""
    callback: AgentExecutorAsyncIteratorCallbackHandler
    """AgentExecutor callback."""
    intermediate_steps: List[Tuple[AgentAction, Union[BaseToolOutput, str]]] = []
    """intermediate_steps to store the data to be processed."""
    history: List[Union[List, Tuple, Dict]] = []
    """user message history"""

    mcp_connections: dict[str, StdioConnection | SSEConnection] = None
    """MCP connections."""

    class Config:
        arbitrary_types_allowed = True

    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    @staticmethod
    async def create_mcp_client(connections: dict[str, StdioConnection | SSEConnection] = None) -> MultiServerMCPClient:
        """

        # 更新协议 transport == "stdio" 的 config，增加env变量
        "env": {
            **os.environ,
            "PYTHONHASHSEED": "0",
        },
        """ 
        for server_name, connection in connections.items(): 
            if connection["transport"] == "stdio":
                connection["env"] = {
                    **os.environ,
                    "PYTHONHASHSEED": "0",
                }
              
        # Create client without context manager to keep session alive
        client = MultiServerMCPClient(connections)
        await client.__aenter__()
        return client

    @staticmethod
    def paser_all_tools(
            tool: Dict[str, Any], callbacks: List[BaseCallbackHandler] = []
    ) -> AdapterAllTool:
        platform_params = {}
        if tool["type"] in tool:
            platform_params = tool[tool["type"]]

        if tool["type"] in TOOL_STRUCT_TYPE_TO_TOOL_CLASS:
            all_tool = TOOL_STRUCT_TYPE_TO_TOOL_CLASS[tool["type"]](
                name=tool["type"], platform_params=platform_params, callbacks=callbacks
            )
            return all_tool
        else:
            raise ValueError(f"Unknown tool type: {tool['type']}")

    @classmethod
    def create_agent_executor(
            cls,
            agent_type: str,
            agents_registry: Callable,
            llm: BaseLanguageModel,
            *,
            intermediate_steps: List[Tuple[AgentAction, BaseToolOutput]] = [],
            history: List[Union[List, Tuple, Dict]] = [],
            tools: Sequence[
                Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]
            ] = None,
            mcp_connections: dict[str, StdioConnection | SSEConnection] = None,
            callbacks: List[BaseCallbackHandler] = None,
            **kwargs: Any,
    ) -> "PlatformToolsRunnable":
        """Create an ZhipuAI Assistant and instantiate the Runnable."""
        if not isinstance(llm, ChatPlatformAI):
            raise ValueError

        callback = AgentExecutorAsyncIteratorCallbackHandler()
        final_callbacks = [callback] + llm.callbacks
        if callbacks:
            final_callbacks.extend(callbacks)

        llm.callbacks = final_callbacks
        llm_with_all_tools = None

        temp_tools = []
        if tools:
            llm_with_all_tools = [_get_assistants_tool(tool) for tool in tools]

            temp_tools.extend(
                [
                    t.copy(update={"callbacks": final_callbacks})
                    for t in tools
                    if not _is_assistants_builtin_tool(t)
                ]
            )

            assistants_builtin_tools = []
            for t in tools:
                # TODO: platform tools built-in for all tools,
                #       load with langchain_chatchat/agents/all_tools_agent.py:108
                # AdapterAllTool implements it
                if _is_assistants_builtin_tool(t):
                    assistants_builtin_tools.append(cls.paser_all_tools(t, final_callbacks))
            temp_tools.extend(assistants_builtin_tools)


        import nest_asyncio
        nest_asyncio.apply()
        if sys.version_info < (3, 10):
            loop = asyncio.get_event_loop()
        else:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()

            asyncio.set_event_loop(loop)
        client = loop.run_until_complete(cls.create_mcp_client(mcp_connections))
        # Get tools
        mcp_tools = client.get_tools()
        agent_executor = agents_registry(
            agent_type=agent_type,
            llm=llm,
            callbacks=final_callbacks,
            tools=temp_tools,
            mcp_tools=mcp_tools,
            llm_with_platform_tools=llm_with_all_tools,
            verbose=True,
            **kwargs,
        )

        return cls(
            agent_type=agent_type,
            agent_executor=agent_executor,
            callback=callback,
            intermediate_steps=intermediate_steps,
            history=history,
            **kwargs,
        )

    def invoke(
            self, chat_input: str,
            config: Optional[RunnableConfig] = None
    ) -> AsyncIterable[OutputType]:
        async def chat_iterator() -> AsyncIterable[OutputType]:
            history_message = []
            if self.history:
                _history = [History.from_data(h) for h in self.history]
                _chat_history = [h.to_msg_tuple() for h in _history]

                history_message.extend(convert_to_messages(_chat_history))

            task = asyncio.create_task(
                wrap_done(
                    self.agent_executor.ainvoke(
                        {
                            "input": chat_input,
                            "chat_history": history_message,
                            "intermediate_steps": self.intermediate_steps
                        }
                    ),
                    self.callback.done,
                )
            )

            async for chunk in self.callback.aiter():
                data = json.loads(chunk)
                class_status = None
                if data["status"] == AgentStatus.llm_start:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data["run_id"],
                        status=data["status"],
                        text=data["text"],
                    )

                elif data["status"] == AgentStatus.llm_new_token:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data["run_id"],
                        status=data["status"],
                        text=data["text"],
                    )
                elif data["status"] == AgentStatus.llm_end:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data["run_id"],
                        status=data["status"],
                        text=data["text"],
                    )
                elif data["status"] == AgentStatus.agent_action:
                    class_status = PlatformToolsAction(
                        run_id=data["run_id"], status=data["status"], **data["action"]
                    )

                elif data["status"] == AgentStatus.tool_start:
                    class_status = PlatformToolsActionToolStart(
                        run_id=data["run_id"],
                        status=data["status"],
                        tool_input=data["tool_input"],
                        tool=data["tool"],
                    )

                elif data["status"] == AgentStatus.tool_require_approval:
                    class_status = PlatformToolsApprove(
                        run_id=data["run_id"],
                        status=data["status"],
                        tool_input=data["tool_input"],
                        tool=data["tool"],
                    )

                elif data["status"] in [AgentStatus.tool_end]:
                    class_status = PlatformToolsActionToolEnd(
                        run_id=data["run_id"],
                        status=data["status"],
                        tool=data["tool"],
                        tool_output=str(data["tool_output"]),
                    )
                elif data["status"] == AgentStatus.agent_finish:
                    class_status = PlatformToolsFinish(
                        run_id=data["run_id"],
                        status=data["status"],
                        **data["finish"],
                    )

                elif data["status"] == AgentStatus.agent_finish:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data["run_id"],
                        status=data["status"],
                        text=data["outputs"]["output"],
                    )

                elif data["status"] == AgentStatus.error:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data.get("run_id", "abc"),
                        status=data["status"],
                        text=json.dumps(data, ensure_ascii=False),
                    )
                elif data["status"] == AgentStatus.chain_start:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data["run_id"],
                        status=data["status"],
                        text="",
                    )
                elif data["status"] == AgentStatus.chain_end:
                    class_status = PlatformToolsLLMStatus(
                        run_id=data["run_id"],
                        status=data["status"],
                        text=data["outputs"]["output"],
                    )

                yield class_status

            await task

            # if self.callback.out:
            self.history.append({"role": "user", "content": chat_input})
            self.history.append(
                {"role": "assistant", "content": self.callback.outputs["output"]}
            )
            self.intermediate_steps.extend(self.callback.intermediate_steps)

        return chat_iterator()

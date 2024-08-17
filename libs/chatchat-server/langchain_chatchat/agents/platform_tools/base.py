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
from pydantic.v1 import Field, validator
from typing_extensions import ClassVar
from zhipuai.core import PYDANTIC_V2, BaseModel, ConfigDict

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
from langchain_chatchat.agents.agents_registry.agents_registry import agents_registry
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
    PlatformToolsLLMStatus,
)
from langchain_chatchat.callbacks.agent_callback_handler import (
    AgentExecutorAsyncIteratorCallbackHandler,
    AgentStatus,
)
from langchain_chatchat.chat_models import ChatPlatformAI
from langchain_chatchat.chat_models.base import ChatPlatformAI
from langchain_chatchat.utils import History

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
    """ZhipuAI AgentExecutor callback."""
    intermediate_steps: List[Tuple[AgentAction, BaseToolOutput]] = []
    """intermediate_steps to store the data to be processed."""
    history: List[Union[List, Tuple, Dict]] = []
    """user message history"""

    class Config:
        arbitrary_types_allowed = True

    if PYDANTIC_V2:
        model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

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
            llm: BaseLanguageModel,
            *,
            intermediate_steps: List[Tuple[AgentAction, BaseToolOutput]] = [],
            history: List[Union[List, Tuple, Dict]] = [],
            tools: Sequence[
                Union[Dict[str, Any], Type[BaseModel], Callable, BaseTool]
            ] = None,
            temperature: float = 0.7,
            **kwargs: Any,
    ) -> "PlatformToolsRunnable":
        """Create an ZhipuAI Assistant and instantiate the Runnable."""
        if not isinstance(llm, ChatPlatformAI):
            raise ValueError

        callback = AgentExecutorAsyncIteratorCallbackHandler()
        callbacks = [callback]

        llm_with_all_tools = None

        temp_tools = []
        if tools:
            llm_with_all_tools = [_get_assistants_tool(tool) for tool in tools]

            temp_tools.extend(
                [
                    t.copy(update={"callbacks": callbacks})
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
                    assistants_builtin_tools.append(cls.paser_all_tools(t, callbacks))
            temp_tools.extend(assistants_builtin_tools)

        agent_executor = agents_registry(
            agent_type=agent_type,
            llm=llm,
            callbacks=callbacks,
            tools=temp_tools,
            llm_with_platform_tools=llm_with_all_tools,
            verbose=True,
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
            self, chat_input: str, config: Optional[RunnableConfig] = None
    ) -> AsyncIterable[OutputType]:
        async def chat_iterator() -> AsyncIterable[OutputType]:
            history_message = []
            if self.history:
                _history = [History.from_data(h) for h in self.history]
                chat_history = [h.to_msg_tuple() for h in _history]

                history_message = convert_to_messages(chat_history)

            task = asyncio.create_task(
                wrap_done(
                    self.agent_executor.ainvoke(
                        {
                            "input": chat_input,
                            "chat_history": history_message,
                            "agent_scratchpad": lambda x: format_to_platform_tool_messages(
                                self.intermediate_steps
                            ),
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

            if self.callback.out:
                self.history.append({"role": "user", "content": chat_input})
                self.history.append(
                    {"role": "assistant", "content": self.callback.outputs["output"]}
                )
                self.intermediate_steps.extend(self.callback.intermediate_steps)

        return chat_iterator()

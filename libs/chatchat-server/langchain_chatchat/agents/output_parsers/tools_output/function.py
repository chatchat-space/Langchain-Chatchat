# -*- coding: utf-8 -*-
import logging
from collections import deque
from typing import Deque, List, Union

from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import (
    BaseMessage,
)
from langchain_core.utils.json import parse_partial_json

from langchain_chatchat.agent_toolkits.all_tools.struct_type import (
    AdapterAllToolStructType,
)
from langchain_chatchat.agents.output_parsers.tools_output.base import (
    PlatformToolsMessageToolCall,
    PlatformToolsMessageToolCallChunk,
)

logger = logging.getLogger(__name__)


def _best_effort_parse_function_tool_calls(
    tool_call_chunks: List[dict],
) -> List[Union[PlatformToolsMessageToolCall, PlatformToolsMessageToolCallChunk]]:
    function_chunk: List[
        Union[PlatformToolsMessageToolCall, PlatformToolsMessageToolCallChunk]
    ] = []
    # Best-effort parsing allready parsed tool calls
    for function in tool_call_chunks:
        if function["name"] not in AdapterAllToolStructType.__members__.values():
            if isinstance(function["args"], str):
                args_ = parse_partial_json(function["args"])
            else:
                args_ = function["args"]
            if not isinstance(args_, dict):
                raise ValueError("Malformed args.")

            if len(args_.keys()) > 0:
                function_chunk.append(
                    PlatformToolsMessageToolCall(
                        name=function["name"],
                        args=args_,
                        id=function["id"],
                    )
                )
            else:
                function_chunk.append(
                    PlatformToolsMessageToolCallChunk(
                        name=function["name"],
                        args=args_,
                        id=function["id"],
                        index=function.get("index"),
                    )
                )

    return function_chunk


def _paser_function_chunk_input(
    message: BaseMessage,
    function_chunk: List[Union[PlatformToolsMessageToolCall, PlatformToolsMessageToolCallChunk]],
) -> Deque[ToolAgentAction]:
    try:
        function_action_result_stack: Deque[ToolAgentAction] = deque()
        for _chunk in function_chunk:
            if isinstance(_chunk, PlatformToolsMessageToolCall):
                function_name = _chunk.name
                _tool_input = _chunk.args
                tool_call_id = _chunk.id if _chunk.id else "abc"
                if "__arg1" in _tool_input:
                    tool_input = _tool_input["__arg1"]
                else:
                    tool_input = _tool_input

                content_msg = (
                    f"responded: {message.content}\n" if message.content else "\n"
                )
                log = f"\nInvoking: `{function_name}` with `{tool_input}`\n{content_msg}\n"

                function_action_result_stack.append(
                    ToolAgentAction(
                        tool=function_name,
                        tool_input=tool_input,
                        log=log,
                        message_log=[message],
                        tool_call_id=tool_call_id,
                    )
                )

        return function_action_result_stack

    except Exception as e:
        logger.error(f"Error parsing function_chunk: {e}", exc_info=True)
        raise OutputParserException(f"Error parsing function_chunk: {e} ")

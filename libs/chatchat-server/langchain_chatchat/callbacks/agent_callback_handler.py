# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Generic, Iterable, TypeVar

import asyncio
import json
from typing import List, Tuple, Any, Awaitable, Callable, Dict, Optional
from uuid import UUID
from enum import Enum
from langchain_core.load import dumpd, dumps, load, loads

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from langchain_community.callbacks.human import HumanRejectedException
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult

from langchain_chatchat.agent_toolkits import BaseToolOutput
from langchain_chatchat.callbacks.core.protocol import AgentBackend
from langchain_chatchat.utils import History

# Define TypeVars for input and output types
T = TypeVar("T")
R = TypeVar("R")


class ApprovalMethod(Enum):
    CLI = "cli"
    BACKEND = "backend"


class AgentStatus:
    chain_start: int = 0
    llm_start: int = 1
    llm_new_token: int = 2
    llm_end: int = 3
    agent_action: int = 4
    agent_finish: int = 5
    tool_require_approval: int = 6
    tool_start: int = 7
    tool_end: int = 8
    error: int = -1
    chain_end: int = -999


class AgentExecutorAsyncIteratorCallbackHandler(AsyncIteratorCallbackHandler):
    approval_method: ApprovalMethod | None = None
    backend: AgentBackend | None = None
    raise_error: bool = True

    def __init__(
            self,
            **kwargs
    ):
        super().__init__()
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
        self.out = False
        self.intermediate_steps: List[Tuple[AgentAction, BaseToolOutput]] = []
        self.outputs: Dict[str, Any] = {}
        self.approval_method = kwargs.get("approval_method", ApprovalMethod.CLI)
        self.backend = kwargs.get("backend", None)

    async def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        data = {
            "status": AgentStatus.llm_start,
            "text": "",
        }
        self.out = False
        self.done.clear()
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        special_tokens = ["\nAction:", "\nObservation:", "<|observation|>"]
        for stoken in special_tokens:
            if stoken in token:
                before_action = token.split(stoken)[0]
                data = {
                    "status": AgentStatus.llm_new_token,
                    "text": before_action + "\n",
                }
                self.done.clear()
                self.queue.put_nowait(dumps(data, pretty=True))

                break

        if token is not None and token != "":
            data = {
                "run_id": str(kwargs["run_id"]),
                "status": AgentStatus.llm_new_token,
                "text": token,
            }
            self.done.clear()
            self.queue.put_nowait(dumps(data, pretty=True))

    async def on_chat_model_start(
            self,
            serialized: Dict[str, Any],
            messages: List[List],
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> None:
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.llm_start,
            "text": "",
        }
        self.done.clear()
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        data = {
            "run_id": str(kwargs["run_id"]),
            "status": AgentStatus.llm_end,
            "text": response.generations[0][0].message.content,
        }

        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_llm_error(
            self, error: Exception | KeyboardInterrupt, **kwargs: Any
    ) -> None:
        data = {
            "status": AgentStatus.error,
            "text": str(error),
        }
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_tool_start(
            self,
            serialized: Dict[str, Any],
            input_str: str,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> None:
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.tool_start,
            "tool": serialized["name"],
            "tool_input": input_str,
        }

        if self.approval_method is ApprovalMethod.CLI:

            # self.done.clear()
            # self.queue.put_nowait(dumps(data, pretty=True))
            # if not await _adefault_approve(input_str):
            #     raise HumanRejectedException(
            #         f"Inputs {input_str} to tool {serialized} were rejected."
            #     )
            pass
        elif self.approval_method is ApprovalMethod.BACKEND:
            pass
        else:
            raise ValueError("Approval method not recognized.")

        self.done.clear()
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_tool_end(
            self,
            output: Any,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        """Run when tool ends running."""
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.tool_end,
            "tool": kwargs["name"],
            "tool_output": str(output),
        }
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_tool_error(
            self,
            error: BaseException,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        """Run when tool errors."""
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.error,
            "tool_output": str(error),
            "is_error": True,
        }

        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_agent_action(
            self,
            action: AgentAction,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.agent_action,
            "action": {
                "tool": action.tool,
                "tool_input": action.tool_input,
                "log": action.log,
            },
        }
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_agent_finish(
            self,
            finish: AgentFinish,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        if isinstance(finish.return_values["output"], str):
            if "Thought:" in finish.return_values["output"]:
                finish.return_values["output"] = finish.return_values["output"].replace(
                    "Thought:", ""
                )

        finish.return_values["output"] = str(finish.return_values["output"])

        data = {
            "run_id": str(run_id),
            "status": AgentStatus.agent_finish,
            "finish": {
                "return_values": finish.return_values,
                "log": finish.log,
            },
        }

        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_chain_start(
            self,
            serialized: Dict[str, Any],
            inputs: Dict[str, Any],
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> None:
        """Run when chain starts running."""
        if "agent_scratchpad" in inputs:
            del inputs["agent_scratchpad"]
        if "chat_history" in inputs:
            inputs["chat_history"] = [
                History.from_message(message).to_msg_tuple()
                for message in inputs["chat_history"]
            ]
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.chain_start,
            "inputs": inputs,
            "parent_run_id": parent_run_id,
            "tags": tags,
            "metadata": metadata,
        }

        self.done.clear()
        self.out = False
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_chain_error(
            self,
            error: BaseException,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        """Run when chain errors."""
        data = {
            "run_id": str(run_id),
            "status": AgentStatus.error,
            "error": str(error),
        }
        self.queue.put_nowait(dumps(data, pretty=True))

    async def on_chain_end(
            self,
            outputs: Dict[str, Any],
            *,
            run_id: UUID,
            parent_run_id: UUID | None = None,
            tags: List[str] | None = None,
            **kwargs: Any,
    ) -> None:
        # TODO agent params of PlatformToolsAgentExecutor or AgentExecutor  enable return_intermediate_steps=True,
        if "intermediate_steps" in outputs:
            self.intermediate_steps = outputs["intermediate_steps"]
            self.outputs = outputs
            del outputs["intermediate_steps"]

        outputs["output"] = str(outputs["output"])

        data = {
            "run_id": str(run_id),
            "status": AgentStatus.chain_end,
            "outputs": outputs,
            "parent_run_id": parent_run_id,
            "tags": tags,
        }
        self.queue.put_nowait(dumps(data, pretty=True))
        self.out = True
        # self.done.set()


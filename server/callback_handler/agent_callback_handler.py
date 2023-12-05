from __future__ import annotations
from uuid import UUID
import json
from langchain.schema import AgentFinish, AgentAction
import asyncio
from typing import Any, AsyncIterator, Dict, List, Literal, Union, cast, Optional
from langchain_core.outputs import LLMResult
from langchain.callbacks.base import AsyncCallbackHandler

def dumps(obj: Dict) -> str:
    return json.dumps(obj, ensure_ascii=False)


class Status:
    start: int = 1
    running: int = 2
    complete: int = 3
    agent_action: int = 4
    agent_finish: int = 5
    error: int = 6
    tool_finish: int = 7


class CustomAsyncIteratorCallbackHandler(AsyncCallbackHandler):
    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
        self.cur_tool = {}
        self.out = True

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
        print("on_tool_start")

    async def on_tool_end(
            self,
            output: str,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        print("on_tool_end")
    async def on_tool_error(self, error: Exception | KeyboardInterrupt, *, run_id: UUID,
                            parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.error,
            error=str(error),
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        special_tokens = ["Action", "<|observation|>"]
        for stoken in special_tokens:
            if stoken in token:
                before_action = token.split(stoken)[0]
                self.cur_tool.update(
                    status=Status.running,
                    llm_token=before_action + "\n",
                )
                self.queue.put_nowait(dumps(self.cur_tool))
                self.out = False
                break

        if token is not None and token != "" and self.out:
            self.cur_tool.update(
                status=Status.running,
                llm_token=token,
            )
            self.queue.put_nowait(dumps(self.cur_tool))

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.start,
            llm_token="",
        )
        self.queue.put_nowait(dumps(self.cur_tool))

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
        self.cur_tool.update(
            status=Status.start,
            llm_token="",
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.complete,
            llm_token="",
        )
        self.out = True
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.error,
            error=str(error),
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_agent_action(
            self,
            action: AgentAction,
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        self.cur_tool.update(
            status=Status.agent_action,
            tool_name=action.tool,
            tool_input=action.tool_input,
        )
        self.queue.put_nowait(dumps(self.cur_tool))
    async def on_agent_finish(
            self, finish: AgentFinish, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        self.cur_tool.update(
            status=Status.agent_finish,
            agent_finish=finish.return_values["output"],
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def aiter(self) -> AsyncIterator[str]:
        while not self.queue.empty() or not self.done.is_set():
            done, other = await asyncio.wait(
                [
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if other:
                other.pop().cancel()
            token_or_done = cast(Union[str, Literal[True]], done.pop().result())
            if token_or_done is True:
                break
            yield token_or_done

from typing import Any, Coroutine, Dict, List, Optional, Union
from uuid import UUID
from langchain.callbacks import AsyncIteratorCallbackHandler
import json
from langchain.schema.agent import AgentFinish

from langchain.schema.output import LLMResult


def dumps(obj: Dict) -> str:
    return json.dumps(obj, ensure_ascii=False)


class Status:
    start: int = 1
    running: int = 2
    complete: int = 3
    agent_finish: int = 4
    error: int = 5


class CustomAsyncIteratorCallbackHandler(AsyncIteratorCallbackHandler):
    def __init__(self):
        super().__init__()
        self.cur_tool = {}
        self.done.clear()

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, metadata: Dict[str, Any] | None = None, **kwargs: Any) -> None:
        self.cur_tool = {
            "tool_name": serialized["name"],
            "input_str": input_str,
            "output_str": "",
            "status": Status.start,
            "run_id": run_id.hex,
            "llm_token": "",
            "error": "",
        }
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_tool_end(self, output: str, *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.complete,
            llm_token="",
            output_str=output,
        )
        self.queue.put_nowait(dumps(self.cur_tool))
        self.cur_tool = {}

    async def on_tool_error(self, error: Exception | KeyboardInterrupt, *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.error,
            error=str(error),
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Coroutine[Any, Any, None]:
        self.cur_tool.update(
            status=Status.start,
            llm_token="",
        )
        self.queue.put_nowait(dumps(self.cur_tool))
    
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token:
            self.cur_tool.update(
                status=Status.running,
                llm_token=token,
            )
            self.queue.put_nowait(dumps(self.cur_tool))
    
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.complete,
            llm_token="",
        )
        self.queue.put_nowait(dumps(self.cur_tool))
    
    async def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.error,
            error=str(error),
        )
        self.queue.put_nowait(dumps(self.cur_tool))
    
    async def on_agent_finish(self, finish: AgentFinish, *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> None:
        data = {
            "status": Status.agent_finish,
            "finanl_output": finish,
        }
        self.queue.put_nowait(dumps(data))
        self.done.set()

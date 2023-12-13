from __future__ import annotations
from uuid import UUID
from langchain.callbacks import AsyncIteratorCallbackHandler
import json
import asyncio
from typing import Any, Dict, List, Optional

from langchain.schema import AgentFinish, AgentAction
from langchain.schema.output import LLMResult


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


class CustomAsyncIteratorCallbackHandler(AsyncIteratorCallbackHandler):
    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
        self.cur_tool = {}
        self.out = True

    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *, run_id: UUID,
                            parent_run_id: UUID | None = None, tags: List[str] | None = None,
                            metadata: Dict[str, Any] | None = None, **kwargs: Any) -> None:

        # 对于截断不能自理的大模型，我来帮他截断
        stop_words = ["Observation:", "Thought","\"","（", "\n","\t"]
        for stop_word in stop_words:
            index = input_str.find(stop_word)
            if index != -1:
                input_str = input_str[:index]
                break

        self.cur_tool = {
            "tool_name": serialized["name"],
            "input_str": input_str,
            "output_str": "",
            "status": Status.agent_action,
            "run_id": run_id.hex,
            "llm_token": "",
            "final_answer": "",
            "error": "",
        }
        # print("\nInput Str:",self.cur_tool["input_str"])
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_tool_end(self, output: str, *, run_id: UUID, parent_run_id: UUID | None = None,
                          tags: List[str] | None = None, **kwargs: Any) -> None:
        self.out = True ## 重置输出
        self.cur_tool.update(
            status=Status.tool_finish,
            output_str=output.replace("Answer:", ""),
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_tool_error(self, error: Exception | KeyboardInterrupt, *, run_id: UUID,
                            parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.error,
            error=str(error),
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    # async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
    #     if "Action" in token: ## 减少重复输出
    #         before_action = token.split("Action")[0]
    #         self.cur_tool.update(
    #             status=Status.running,
    #             llm_token=before_action + "\n",
    #         )
    #         self.queue.put_nowait(dumps(self.cur_tool))
    #
    #         self.out = False
    #
    #     if token and self.out:
    #         self.cur_tool.update(
    #                 status=Status.running,
    #                 llm_token=token,
    #         )
    #         self.queue.put_nowait(dumps(self.cur_tool))
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

        if token and self.out:
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
            llm_token="\n",
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        self.cur_tool.update(
            status=Status.error,
            error=str(error),
        )
        self.queue.put_nowait(dumps(self.cur_tool))

    async def on_agent_finish(
            self, finish: AgentFinish, *, run_id: UUID, parent_run_id: Optional[UUID] = None,
            tags: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> None:
        # 返回最终答案
        self.cur_tool.update(
            status=Status.agent_finish,
            final_answer=finish.return_values["output"],
        )
        self.queue.put_nowait(dumps(self.cur_tool))
        self.cur_tool = {}

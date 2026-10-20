"""Preserve MiniMax reasoning when using the pinned chat integration."""

from typing import Any, AsyncIterator, Iterator

from langchain_core.messages import AIMessageChunk, BaseMessage, BaseMessageChunk
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_openai import ChatOpenAI

from langchain_chatchat.chat_models.base import _convert_delta_to_message_chunk


class MiniMaxChatOpenAI(ChatOpenAI):
    def _create_message_dicts(
        self, messages: list[BaseMessage], stop: list[str] | None
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        payload, params = super()._create_message_dicts(messages, stop)
        for message, item in zip(messages, payload):
            if (
                item["role"] == "assistant"
                and "reasoning_content" in message.additional_kwargs
            ):
                item["reasoning_content"] = message.additional_kwargs[
                    "reasoning_content"
                ]
        return payload, params

    def _create_chat_result(self, response: Any) -> ChatResult:
        if not isinstance(response, dict):
            response = response.dict()
        result = super()._create_chat_result(response)
        for generation, choice in zip(result.generations, response["choices"]):
            message = choice["message"]
            if "reasoning_content" in message:
                generation.message.additional_kwargs["reasoning_content"] = message[
                    "reasoning_content"
                ]
        return result

    @staticmethod
    def _generation_chunk(
        chunk: Any, default_class: type[BaseMessageChunk]
    ) -> ChatGenerationChunk | None:
        if not isinstance(chunk, dict):
            chunk = chunk.dict()
        if not chunk["choices"]:
            return None
        choice = chunk["choices"][0]
        info = {
            key: choice[key]
            for key in ("finish_reason", "logprobs")
            if choice.get(key) is not None
        }
        return ChatGenerationChunk(
            message=_convert_delta_to_message_chunk(choice["delta"], default_class),
            generation_info=info or None,
        )

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}
        default_class: type[BaseMessageChunk] = AIMessageChunk
        with self.client.create(messages=message_dicts, **params) as response:
            for chunk in response:
                generation = self._generation_chunk(chunk, default_class)
                if generation is None:
                    continue
                default_class = generation.message.__class__
                if run_manager:
                    run_manager.on_llm_new_token(generation.text, chunk=generation)
                yield generation

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}
        default_class: type[BaseMessageChunk] = AIMessageChunk
        async with await self.async_client.create(
            messages=message_dicts, **params
        ) as response:
            async for chunk in response:
                generation = self._generation_chunk(chunk, default_class)
                if generation is None:
                    continue
                default_class = generation.message.__class__
                if run_manager:
                    await run_manager.on_llm_new_token(
                        generation.text, chunk=generation
                    )
                yield generation

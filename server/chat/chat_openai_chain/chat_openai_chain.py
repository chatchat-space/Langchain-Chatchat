from __future__ import annotations
from abc import ABC
from typing import Any, Dict, List, Optional
from langchain.chains.base import Chain
from langchain.schema import (
    BaseMessage,
    messages_from_dict,
    LLMResult
)
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
    Callbacks,
)
from server.model.chat_openai_chain import OpenAiChatMsgDto, OpenAiMessageDto, BaseMessageDto


def convert_message_processors(message_data: List[OpenAiMessageDto]) -> List[BaseMessage]:
    """
    前端消息传输对象DTO转换为chat消息传输对象DTO
    :param message_data:
    :return:
    """
    messages = []
    for message_datum in message_data:
        messages.append(message_datum.dict())
    return messages_from_dict(messages)


class BaseChatOpenAIChain(Chain, ABC):
    chat: ChatOpenAI
    message_dto_key: str = "message_dto"  #: :meta private:
    output_key: str = "text"  #: :meta private:

    @classmethod
    def from_chain(
            cls,
            model_name: str,
            streaming: Optional[bool],
            verbose: Optional[bool],
            callbacks: Optional[Callbacks],
            openai_api_key: Optional[str],
            # openai_api_base: Optional[str],
            **kwargs: Any,
    ) -> BaseChatOpenAIChain:
        chat = ChatOpenAI(
            streaming=streaming,
            verbose=verbose,
            callbacks=callbacks,
            openai_api_key=openai_api_key,
            # openai_api_base=openai_api_base,
            model_name=model_name
        )
        return cls(chat=chat, **kwargs)

    @property
    def _chain_type(self) -> str:
        return "BaseChatOpenAIChain"

    @property
    def input_keys(self) -> List[str]:
        return [self.message_dto_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def create_outputs(self, response: LLMResult) -> List[Dict[str, str]]:
        """Create outputs from response."""
        return [
            # Get the text of the top generated string.
            {self.output_key: generation[0].text}
            for generation in response.generations
        ]

    def _call(
            self,
            inputs: Dict[str, OpenAiChatMsgDto],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        msg_dto = inputs[self.message_dto_key]
        openai_messages_dto = convert_message_processors(msg_dto.messages)

        _text = "openai_messages_dto after formatting:\n" + str(openai_messages_dto)
        if run_manager:
            run_manager.on_text(_text, end="\n", verbose=self.verbose)

        response = self.chat(messages=openai_messages_dto, stop=msg_dto.stop)
        return self.create_outputs(response)[0]

    async def _acall(
            self,
            inputs: Dict[str, OpenAiChatMsgDto],
            run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        msg_dto = inputs[self.message_dto_key]

        openai_messages_dto = convert_message_processors(msg_dto.messages)

        _text = "openai_messages_dto after formatting:\n" + str(openai_messages_dto)
        if run_manager:
            run_manager.on_text(_text, end="\n", verbose=self.verbose)

        response = await self.chat(messages=openai_messages_dto, stop=msg_dto.stop)
        return self.create_outputs(response)[0]


if __name__ == "__main__":
    from langchain.callbacks import AsyncIteratorCallbackHandler
    import json

    # Convert instances of the classes to dictionaries
    message_dto1 = OpenAiMessageDto(type="human", data=BaseMessageDto(content="Hello!"))
    message_dto2 = OpenAiMessageDto(type="system", data=BaseMessageDto(content="hi!"))
    chat_msg_dto = OpenAiChatMsgDto(model_name="gpt-3.5-turbo", messages=[message_dto1, message_dto2])

    chat_msg_json = json.dumps(chat_msg_dto.dict(), indent=2)

    print("OpenAiChatMsgDto JSON:")
    print(chat_msg_json)

    callback = AsyncIteratorCallbackHandler()

    chains = BaseChatOpenAIChain.from_chain(
        streaming=chat_msg_dto.stream,
        verbose=True,
        callbacks=[callback],
        openai_api_key="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",
        model_name=chat_msg_dto.model_name

    )

    out = chains({"message_dto": chat_msg_dto})

    print(out)

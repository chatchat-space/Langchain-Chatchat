from abc import ABC
from langchain.chains.base import Chain
from typing import Any, Dict, List, Optional, Generator, Collection
from models.loader import LoaderCheckPoint
from langchain.callbacks.manager import CallbackManagerForChainRun
from models.base import (BaseAnswer,
                         RemoteRpcModel,
                         AnswerResult,
                         AnswerResultStream,
                         AnswerResultQueueSentinelTokenListenerQueue)
import torch
import transformers


def _build_message_template() -> Dict[str, str]:
    """
    :return: 结构
    """
    return {
        "role": "",
        "content": "",
    }


# 将历史对话数组转换为文本格式
def build_message_list(query, history: List[List[str]]) -> Collection[Dict[str, str]]:
    build_messages: Collection[Dict[str, str]] = []
    for i, (old_query, response) in enumerate(history):
        user_build_message = _build_message_template()
        user_build_message['role'] = 'user'
        user_build_message['content'] = old_query
        system_build_message = _build_message_template()
        system_build_message['role'] = 'system'
        system_build_message['content'] = response
        build_messages.append(user_build_message)
        build_messages.append(system_build_message)

    user_build_message = _build_message_template()
    user_build_message['role'] = 'user'
    user_build_message['content'] = query
    build_messages.append(user_build_message)
    return build_messages


class FastChatOpenAILLMChain(RemoteRpcModel, Chain, ABC):
    api_base_url: str = "http://localhost:8000/v1"
    model_name: str = "chatglm-6b"
    max_token: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    checkPoint: LoaderCheckPoint = None
    # history = []
    history_len: int = 10
    api_key: str = ""

    streaming_key: str = "streaming"  #: :meta private:
    history_key: str = "history"  #: :meta private:
    prompt_key: str = "prompt"  #: :meta private:
    output_key: str = "answer_result_stream"  #: :meta private:

    def __init__(self,
                 checkPoint: LoaderCheckPoint = None,
                 #  api_base_url:str="http://localhost:8000/v1",
                 #  model_name:str="chatglm-6b",
                 #  api_key:str=""
                 ):
        super().__init__()
        self.checkPoint = checkPoint

    @property
    def _chain_type(self) -> str:
        return "LLamaLLMChain"

    @property
    def _check_point(self) -> LoaderCheckPoint:
        return self.checkPoint

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return [self.prompt_key]

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    @property
    def _api_key(self) -> str:
        pass

    @property
    def _api_base_url(self) -> str:
        return self.api_base_url

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def set_api_base_url(self, api_base_url: str):
        self.api_base_url = api_base_url

    def call_model_name(self, model_name):
        self.model_name = model_name

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Generator]:
        generator = self.generatorAnswer(inputs=inputs, run_manager=run_manager)
        return {self.output_key: generator}

    def _generate_answer(self,
                         inputs: Dict[str, Any],
                         run_manager: Optional[CallbackManagerForChainRun] = None,
                         generate_with_callback: AnswerResultStream = None) -> None:

        history = inputs[self.history_key]
        streaming = inputs[self.streaming_key]
        prompt = inputs[self.prompt_key]
        print(f"__call:{prompt}")
        try:

            import openai
            # Not support yet
            # openai.api_key = "EMPTY"
            openai.api_key = self.api_key
            openai.api_base = self.api_base_url
        except ImportError:
            raise ValueError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        # create a chat completion
        completion = openai.ChatCompletion.create(
            model=self.model_name,
            messages=build_message_list(prompt)
        )
        print(f"response:{completion.choices[0].message.content}")
        print(f"+++++++++++++++++++++++++++++++++++")

        history += [[prompt, completion.choices[0].message.content]]
        answer_result = AnswerResult()
        answer_result.history = history
        answer_result.llm_output = {"answer": completion.choices[0].message.content}
        generate_with_callback(answer_result)

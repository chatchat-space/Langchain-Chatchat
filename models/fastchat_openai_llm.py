from abc import ABC
from langchain.chains.base import Chain
from typing import (
    Any, Dict, List, Optional, Generator, Collection, Set,
    Callable,
    Tuple,
    Union)

from models.loader import LoaderCheckPoint
from langchain.callbacks.manager import CallbackManagerForChainRun
from models.base import (BaseAnswer,
                         RemoteRpcModel,
                         AnswerResult,
                         AnswerResultStream,
                         AnswerResultQueueSentinelTokenListenerQueue)
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from pydantic import Extra, Field, root_validator

from openai import (
    ChatCompletion
)

import openai
import logging
import torch
import transformers

logger = logging.getLogger(__name__)


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

    system_build_message = _build_message_template()
    system_build_message['role'] = 'system'
    system_build_message['content'] = "You are a helpful assistant."
    build_messages.append(system_build_message)
    if history:
        for i, (user, assistant) in enumerate(history):
            if user:

                user_build_message = _build_message_template()
                user_build_message['role'] = 'user'
                user_build_message['content'] = user
                build_messages.append(user_build_message)

            if not assistant:
                raise RuntimeError("历史数据结构不正确")
            system_build_message = _build_message_template()
            system_build_message['role'] = 'assistant'
            system_build_message['content'] = assistant
            build_messages.append(system_build_message)

    user_build_message = _build_message_template()
    user_build_message['role'] = 'user'
    user_build_message['content'] = query
    build_messages.append(user_build_message)
    return build_messages


class FastChatOpenAILLMChain(RemoteRpcModel, Chain, ABC):
    client: Any
    """Timeout for requests to OpenAI completion API. Default is 600 seconds."""
    max_retries: int = 6
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

    def _create_retry_decorator(self) -> Callable[[Any], Any]:
        min_seconds = 1
        max_seconds = 60
        # Wait 2^x * 1 second between each retry starting with
        # 4 seconds, then up to 10 seconds, then 10 seconds afterwards
        return retry(
            reraise=True,
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=1, min=min_seconds, max=max_seconds),
            retry=(
                    retry_if_exception_type(openai.error.Timeout)
                    | retry_if_exception_type(openai.error.APIError)
                    | retry_if_exception_type(openai.error.APIConnectionError)
                    | retry_if_exception_type(openai.error.RateLimitError)
                    | retry_if_exception_type(openai.error.ServiceUnavailableError)
            ),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )

    def completion_with_retry(self, **kwargs: Any) -> Any:
        """Use tenacity to retry the completion call."""
        retry_decorator = self._create_retry_decorator()

        @retry_decorator
        def _completion_with_retry(**kwargs: Any) -> Any:
            return self.client.create(**kwargs)

        return _completion_with_retry(**kwargs)

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

        history = inputs.get(self.history_key, [])
        streaming = inputs.get(self.streaming_key, False)
        prompt = inputs[self.prompt_key]
        stop = inputs.get("stop", "stop")
        print(f"__call:{prompt}")
        try:

            # Not support yet
            # openai.api_key = "EMPTY"
            openai.api_key = self.api_key
            openai.api_base = self.api_base_url
            self.client = openai.ChatCompletion
        except AttributeError:
            raise ValueError(
                "`openai` has no `ChatCompletion` attribute, this is likely "
                "due to an old version of the openai package. Try upgrading it "
                "with `pip install --upgrade openai`."
            )
        msg = build_message_list(prompt, history=history)

        if streaming:
            params = {"stream": streaming,
                      "model": self.model_name,
                      "stop": stop}
            out_str = ""
            for stream_resp in self.completion_with_retry(
                    messages=msg,
                    **params
            ):
                role = stream_resp["choices"][0]["delta"].get("role", "")
                token = stream_resp["choices"][0]["delta"].get("content", "")
                out_str += token
                history[-1] = [prompt, out_str]
                answer_result = AnswerResult()
                answer_result.history = history
                answer_result.llm_output = {"answer": out_str}
                generate_with_callback(answer_result)
        else:

            params = {"stream": streaming,
                      "model": self.model_name,
                      "stop": stop}
            response = self.completion_with_retry(
                messages=msg,
                **params
            )
            role = response["choices"][0]["message"].get("role", "")
            content = response["choices"][0]["message"].get("content", "")
            history += [[prompt, content]]
            answer_result = AnswerResult()
            answer_result.history = history
            answer_result.llm_output = {"answer": content}
            generate_with_callback(answer_result)


if __name__ == "__main__":

    chain = FastChatOpenAILLMChain()

    chain.set_api_key("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")
    # chain.set_api_base_url("https://api.openai.com/v1")
    # chain.call_model_name("gpt-3.5-turbo")

    answer_result_stream_result = chain({"streaming": True,
                                         "prompt": "你好",
                                         "history": []
                                         })

    for answer_result in answer_result_stream_result['answer_result_stream']:
        resp = answer_result.llm_output["answer"]
        print(resp)

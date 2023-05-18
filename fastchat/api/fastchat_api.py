"""Wrapper around FastChat APIs."""
from __future__ import annotations

import logging
import sys
import warnings
from typing import (
    AbstractSet,
    Any,
    Callable,
    Collection,
    Dict,
    Generator,
    List,
    Literal,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)

from pydantic import Extra, Field, root_validator
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from langchain.llms.base import BaseLLM
from langchain.schema import Generation, LLMResult
from langchain.utils import get_from_dict_or_env

import requests
import json


logger = logging.getLogger(__name__)
FAST_CHAT_API = "http://localhost:21002/worker_generate_stream"


def _streaming_response_template() -> Dict[str, Any]:
    """
    :return: 响应结构
    """
    return {
        "text": "",
        "error_code": 0,
    }


def _update_response(response: Dict[str, Any], stream_response: Dict[str, Any]) -> None:
    """Update response from the stream response."""
    response["text"] += stream_response["text"]
    response["error_code"] += stream_response["error_code"]


class BaseFastChat(BaseLLM):
    """Wrapper around FastChat large language models."""

    model_name: str = "text-davinci-003"
    """Model name to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    max_new_tokens: int = 200
    stop: int = 20
    batch_size: int = 20
    """Maximum number of retries to make when generating."""
    streaming: bool = False
    """Penalizes repeated tokens."""
    n: int = 1
    """Whether to stream the results or not."""
    allowed_special: Union[Literal["all"], AbstractSet[str]] = set()
    """Set of special tokens that are allowed。"""
    disallowed_special: Union[Literal["all"], Collection[str]] = "all"
    """Set of special tokens that are not allowed。"""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.ignore

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = {field.alias for field in cls.__fields__.values()}

        extra = values.get("model_kwargs", {})
        for field_name in list(values):
            if field_name not in all_required_field_names:
                if field_name in extra:
                    raise ValueError(f"Found {field_name} supplied twice.")
                logger.warning(
                    f"""WARNING! {field_name} is not default parameter.
                    {field_name} was transfered to model_kwargs.
                    Please confirm that {field_name} is what you intended."""
                )
                extra[field_name] = values.pop(field_name)
        values["model_kwargs"] = extra
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling FastChat API."""
        normal_params = {
            "model": self.model_name,
            "prompt": '',
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
        }

        return {**normal_params}

    def _generate(
            self, prompts: List[str], stop: Optional[List[str]] = None
    ) -> LLMResult:
        """Call out to FastChat's endpoint with k unique prompts.

        Args:
            prompts: The prompts to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The full LLM output.

        Example:
            .. code-block:: python

                response = fastchat.generate(["Tell me a joke."])
        """
        # TODO: write a unit test for this
        params = self._invocation_params
        sub_prompts = self.get_sub_prompts(params, prompts)
        choices = []
        token_usage: Dict[str, int] = {}
        headers = {"User-Agent": "fastchat Client"}
        for _prompts in sub_prompts:

            params["prompt"] = _prompts[0]

            if stop is not None:
                if "stop" in params:
                    raise ValueError("`stop` found in both the input and default params.")
                params["stop"] = stop

            if self.streaming:
                if len(_prompts) > 1:
                    raise ValueError("Cannot stream results with multiple prompts.")

                response_template = _streaming_response_template()
                response = requests.post(
                    FAST_CHAT_API,
                    headers=headers,
                    json=params,
                    stream=True,
                    )
                for stream_resp in response.iter_lines(
                        chunk_size=8192, decode_unicode=False, delimiter=b"\0"
                ):
                    if stream_resp:
                        data = json.loads(stream_resp.decode("utf-8"))
                        skip_echo_len = len(_prompts[0])
                        output = data["text"][skip_echo_len:].strip()
                        data["text"] = output
                        self.callback_manager.on_llm_new_token(
                            output,
                            verbose=self.verbose,
                            logprobs=data["error_code"],
                        )
                        _update_response(response_template, data)
                choices.append(response_template)
            else:
                response_template = _streaming_response_template()
                response = requests.post(
                    FAST_CHAT_API,
                    headers=headers,
                    json=params,
                    stream=True,
                    )
                for stream_resp in response.iter_lines(
                        chunk_size=8192, decode_unicode=False, delimiter=b"\0"
                ):
                    if stream_resp:
                        data = json.loads(stream_resp.decode("utf-8"))
                        skip_echo_len = len(_prompts[0])
                        output = data["text"][skip_echo_len:].strip()
                        data["text"] = output
                        _update_response(response_template, data)

                choices.append(response_template)

        return self.create_llm_result(choices, prompts, token_usage)

    async def _agenerate(
            self, prompts: List[str], stop: Optional[List[str]] = None
    ) -> LLMResult:
        """Call out to FastChat's endpoint async with k unique prompts."""
        params = self._invocation_params
        sub_prompts = self.get_sub_prompts(params, prompts)
        choices = []
        token_usage: Dict[str, int] = {}

        headers = {"User-Agent": "fastchat Client"}
        for _prompts in sub_prompts:

            params["prompt"] = _prompts[0]
            if stop is not None:
                if "stop" in params:
                    raise ValueError("`stop` found in both the input and default params.")
                params["stop"] = stop

            if self.streaming:
                if len(_prompts) > 1:
                    raise ValueError("Cannot stream results with multiple prompts.")

                response_template = _streaming_response_template()
                response = requests.post(
                    FAST_CHAT_API,
                    headers=headers,
                    json=params,
                    stream=True,
                    )
                for stream_resp in response.iter_lines(
                        chunk_size=8192, decode_unicode=False, delimiter=b"\0"
                ):
                    if stream_resp:
                        data = json.loads(stream_resp.decode("utf-8"))
                        skip_echo_len = len(_prompts[0])
                        output = data["text"][skip_echo_len:].strip()
                        data["text"] = output
                        self.callback_manager.on_llm_new_token(
                            output,
                            verbose=self.verbose,
                            logprobs=data["error_code"],
                        )
                        _update_response(response_template, data)
                choices.append(response_template)
            else:
                response_template = _streaming_response_template()
                response = requests.post(
                    FAST_CHAT_API,
                    headers=headers,
                    json=params,
                    stream=True,
                    )
                for stream_resp in response.iter_lines(
                        chunk_size=8192, decode_unicode=False, delimiter=b"\0"
                ):
                    if stream_resp:
                        data = json.loads(stream_resp.decode("utf-8"))
                        skip_echo_len = len(_prompts[0])
                        output = data["text"][skip_echo_len:].strip()
                        data["text"] = output
                        _update_response(response_template, data)

                choices.append(response_template)

        return self.create_llm_result(choices, prompts, token_usage)

    def get_sub_prompts(
            self,
            params: Dict[str, Any],
            prompts: List[str],
    ) -> List[List[str]]:
        """Get the sub prompts for llm call."""
        if params["max_new_tokens"] == -1:
            if len(prompts) != 1:
                raise ValueError(
                    "max_new_tokens set to -1 not supported for multiple inputs."
                )
            params["max_new_tokens"] = self.max_new_tokens_for_prompt(prompts[0])
        # append pload
        sub_prompts = [
            prompts[i: i + self.batch_size]
            for i in range(0, len(prompts), self.batch_size)
        ]

        return sub_prompts

    def create_llm_result(
            self, choices: Any, prompts: List[str], token_usage: Dict[str, int]
    ) -> LLMResult:
        """Create the LLMResult from the choices and prompts."""
        generations = []
        for i, _ in enumerate(prompts):
            sub_choices = choices[i * self.n: (i + 1) * self.n]
            generations.append(
                [
                    Generation(
                        text=choice["text"],
                        generation_info=dict(
                            finish_reason='over',
                            logprobs=choice["text"],
                        ),
                    )
                    for choice in sub_choices
                ]
            )
        llm_output = {"token_usage": token_usage, "model_name": self.model_name}
        return LLMResult(generations=generations, llm_output=llm_output)

    def stream(self, prompt: str, stop: Optional[List[str]] = None) -> Generator:
        """Call FastChat with streaming flag and return the resulting generator.

        BETA: this is a beta feature while we figure out the right abstraction.
        Once that happens, this interface could change.

        Args:
            prompt: The prompts to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            A generator representing the stream of tokens from OpenAI.

        Example:
            .. code-block:: python

                generator = fastChat.stream("Tell me a joke.")
                for token in generator:
                    yield token
        """
        params = self._invocation_params
        params["prompt"] = prompt
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop

        headers = {"User-Agent": "fastchat Client"}
        response = requests.post(
            FAST_CHAT_API,
            headers=headers,
            json=params,
            stream=True,
        )
        for stream_resp in response.iter_lines(
                chunk_size=8192, decode_unicode=False, delimiter=b"\0"
        ):
            if stream_resp:
                data = json.loads(stream_resp.decode("utf-8"))
                skip_echo_len = len(_prompts[0])
                output = data["text"][skip_echo_len:].strip()
                data["text"] = output
                yield data

    @property
    def _invocation_params(self) -> Dict[str, Any]:
        """Get the parameters used to invoke the model."""
        return self._default_params

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"model_name": self.model_name}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "fastChat"

    def get_num_tokens(self, text: str) -> int:
        """Calculate num tokens with tiktoken package."""
        # tiktoken NOT supported for Python < 3.8
        if sys.version_info[1] < 8:
            return super().get_num_tokens(text)
        try:
            import tiktoken
        except ImportError:
            raise ValueError(
                "Could not import tiktoken python package. "
                "This is needed in order to calculate get_num_tokens. "
                "Please install it with `pip install tiktoken`."
            )

        enc = tiktoken.encoding_for_model(self.model_name)

        tokenized_text = enc.encode(
            text,
            allowed_special=self.allowed_special,
            disallowed_special=self.disallowed_special,
        )

        # calculate the number of tokens in the encoded text
        return len(tokenized_text)

    def modelname_to_contextsize(self, modelname: str) -> int:
        """Calculate the maximum number of tokens possible to generate for a model.

        Args:
            modelname: The modelname we want to know the context size for.

        Returns:
            The maximum context size

        Example:
            .. code-block:: python

                max_new_tokens = openai.modelname_to_contextsize("text-davinci-003")
        """
        model_token_mapping = {
            "vicuna-13b": 2049,
            "koala": 2049,
            "dolly-v2": 2049,
            "oasst": 2049,
            "stablelm": 2049,
        }

        context_size = model_token_mapping.get(modelname, None)

        if context_size is None:
            raise ValueError(
                f"Unknown model: {modelname}. Please provide a valid OpenAI model name."
                "Known models are: " + ", ".join(model_token_mapping.keys())
            )

        return context_size

    def max_new_tokens_for_prompt(self, prompt: str) -> int:
        """Calculate the maximum number of tokens possible to generate for a prompt.

        Args:
            prompt: The prompt to pass into the model.

        Returns:
            The maximum number of tokens to generate for a prompt.

        Example:
            .. code-block:: python

                max_new_tokens = openai.max_token_for_prompt("Tell me a joke.")
        """
        num_tokens = self.get_num_tokens(prompt)

        # get max context size for model by name
        max_size = self.modelname_to_contextsize(self.model_name)
        return max_size - num_tokens


class FastChat(BaseFastChat):
    """Wrapper around OpenAI large language models.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.

    Any parameters that are valid to be passed to the openai.create call can be passed
    in, even if not explicitly saved on this class.

    Example:
        .. code-block:: python

            from langchain.llms import OpenAI
            openai = FastChat(model_name="vicuna")
    """

    @property
    def _invocation_params(self) -> Dict[str, Any]:
        return {**{"model": self.model_name}, **super()._invocation_params}

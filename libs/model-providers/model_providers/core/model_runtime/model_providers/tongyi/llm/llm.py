from typing import Dict, Generator, List, Optional, Type, Union

from dashscope import get_tokenizer
from dashscope.api_entities.dashscope_response import DashScopeAPIResponse
from dashscope.common.error import (
    AuthenticationError,
    InvalidParameter,
    RequestFailure,
    ServiceUnavailableError,
    UnsupportedHTTPMethod,
    UnsupportedModel,
)
from langchain.llms.tongyi import generate_with_retry, stream_generate_with_retry

from model_providers.core.model_runtime.callbacks.base_callback import Callback
from model_providers.core.model_runtime.entities.llm_entities import (
    LLMMode,
    LLMResult,
    LLMResultChunk,
    LLMResultChunkDelta,
)
from model_providers.core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    PromptMessage,
    PromptMessageTool,
    SystemPromptMessage,
    UserPromptMessage,
)
from model_providers.core.model_runtime.errors.invoke import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from model_providers.core.model_runtime.errors.validate import (
    CredentialsValidateFailedError,
)
from model_providers.core.model_runtime.model_providers.__base.large_language_model import (
    LargeLanguageModel,
)

from ._client import EnhanceTongyi


class TongyiLargeLanguageModel(LargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: List[PromptMessage],
        model_parameters: dict,
        tools: Optional[List[PromptMessageTool]] = None,
        stop: Optional[List[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        # invoke model
        return self._generate(
            model, credentials, prompt_messages, model_parameters, stop, stream, user
        )

    def _code_block_mode_wrapper(
        self,
        model: str,
        credentials: dict,
        prompt_messages: List[PromptMessage],
        model_parameters: dict,
        tools: Union[List[PromptMessageTool], None] = None,
        stop: Union[List[str], None] = None,
        stream: bool = True,
        user: Union[str, None] = None,
        callbacks: List[Callback] = None,
    ) -> Union[LLMResult, Generator]:
        """
        Wrapper for code block mode
        """
        block_prompts = """You should always follow the instructions and output a valid {{block}} object.
The structure of the {{block}} object you can found in the instructions, use {"answer": "$your_answer"} as the default structure
if you are not sure about the structure.

<instructions>
{{instructions}}
</instructions>
"""

        code_block = model_parameters.get("response_format", "")
        if not code_block:
            return self._invoke(
                model=model,
                credentials=credentials,
                prompt_messages=prompt_messages,
                model_parameters=model_parameters,
                tools=tools,
                stop=stop,
                stream=stream,
                user=user,
            )

        model_parameters.pop("response_format")
        stop = stop or []
        stop.extend(["\n```", "```\n"])
        block_prompts = block_prompts.replace("{{block}}", code_block)

        # check if there is a system message
        if len(prompt_messages) > 0 and isinstance(
            prompt_messages[0], SystemPromptMessage
        ):
            # override the system message
            prompt_messages[0] = SystemPromptMessage(
                content=block_prompts.replace(
                    "{{instructions}}", prompt_messages[0].content
                )
            )
        else:
            # insert the system message
            prompt_messages.insert(
                0,
                SystemPromptMessage(
                    content=block_prompts.replace(
                        "{{instructions}}",
                        f"Please output a valid {code_block} object.",
                    )
                ),
            )

        mode = self.get_model_mode(model, credentials)
        if mode == LLMMode.CHAT:
            if len(prompt_messages) > 0 and isinstance(
                prompt_messages[-1], UserPromptMessage
            ):
                # add ```JSON\n to the last message
                prompt_messages[-1].content += f"\n```{code_block}\n"
            else:
                # append a user message
                prompt_messages.append(UserPromptMessage(content=f"```{code_block}\n"))
        else:
            prompt_messages.append(AssistantPromptMessage(content=f"```{code_block}\n"))

        response = self._invoke(
            model=model,
            credentials=credentials,
            prompt_messages=prompt_messages,
            model_parameters=model_parameters,
            tools=tools,
            stop=stop,
            stream=stream,
            user=user,
        )

        if isinstance(response, Generator):
            return self._code_block_mode_stream_processor_with_backtick(
                model=model, prompt_messages=prompt_messages, input_generator=response
            )

        return response

    def get_num_tokens(
        self,
        model: str,
        credentials: dict,
        prompt_messages: List[PromptMessage],
        tools: Optional[List[PromptMessageTool]] = None,
    ) -> int:
        """
        Get number of tokens for given prompt messages

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param tools: tools for tool calling
        :return:
        """
        tokenizer = get_tokenizer(model)

        # convert string to token ids
        tokens = tokenizer.encode(self._convert_messages_to_prompt(prompt_messages))

        return len(tokens)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            self._generate(
                model=model,
                credentials=credentials,
                prompt_messages=[
                    UserPromptMessage(content="ping"),
                ],
                model_parameters={
                    "temperature": 0.5,
                },
                stream=False,
            )
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def _generate(
        self,
        model: str,
        credentials: dict,
        prompt_messages: List[PromptMessage],
        model_parameters: dict,
        stop: Optional[List[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        extra_model_kwargs = {}
        if stop:
            extra_model_kwargs["stop"] = stop

        # transform credentials to kwargs for model instance
        credentials_kwargs = self._to_credential_kwargs(credentials)

        client = EnhanceTongyi(
            model_name=model,
            streaming=stream,
            dashscope_api_key=credentials_kwargs["api_key"],
        )

        params = {
            "model": model,
            **model_parameters,
            **credentials_kwargs,
            **extra_model_kwargs,
        }

        mode = self.get_model_mode(model, credentials)

        if mode == LLMMode.CHAT:
            params["messages"] = self._convert_prompt_messages_to_tongyi_messages(
                prompt_messages
            )
        else:
            params["prompt"] = self._convert_messages_to_prompt(prompt_messages)

        if stream:
            responses = stream_generate_with_retry(
                client, stream=True, incremental_output=True, **params
            )

            return self._handle_generate_stream_response(
                model, credentials, responses, prompt_messages
            )

        response = generate_with_retry(
            client,
            **params,
        )
        return self._handle_generate_response(
            model, credentials, response, prompt_messages
        )

    def _handle_generate_response(
        self,
        model: str,
        credentials: dict,
        response: DashScopeAPIResponse,
        prompt_messages: List[PromptMessage],
    ) -> LLMResult:
        """
        Handle llm response

        :param model: model name
        :param credentials: credentials
        :param response: response
        :param prompt_messages: prompt messages
        :return: llm response
        """
        # transform assistant message to prompt message
        assistant_prompt_message = AssistantPromptMessage(content=response.output.text)

        # transform usage
        usage = self._calc_response_usage(
            model,
            credentials,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        # transform response
        result = LLMResult(
            model=model,
            message=assistant_prompt_message,
            prompt_messages=prompt_messages,
            usage=usage,
        )

        return result

    def _handle_generate_stream_response(
        self,
        model: str,
        credentials: dict,
        responses: Generator,
        prompt_messages: List[PromptMessage],
    ) -> Generator:
        """
        Handle llm stream response

        :param model: model name
        :param credentials: credentials
        :param response: response
        :param prompt_messages: prompt messages
        :return: llm response chunk generator result
        """
        for index, response in enumerate(responses):
            resp_finish_reason = response.output.finish_reason
            resp_content = response.output.text
            usage = response.usage

            if resp_finish_reason is None and (
                resp_content is None or resp_content == ""
            ):
                continue

            # transform assistant message to prompt message
            assistant_prompt_message = AssistantPromptMessage(
                content=resp_content if resp_content else "",
            )

            if resp_finish_reason is not None:
                # transform usage
                usage = self._calc_response_usage(
                    model, credentials, usage.input_tokens, usage.output_tokens
                )

                yield LLMResultChunk(
                    model=model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(
                        index=index,
                        message=assistant_prompt_message,
                        finish_reason=resp_finish_reason,
                        usage=usage,
                    ),
                )
            else:
                yield LLMResultChunk(
                    model=model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(
                        index=index, message=assistant_prompt_message
                    ),
                )

    def _to_credential_kwargs(self, credentials: dict) -> dict:
        """
        Transform credentials to kwargs for model instance

        :param credentials:
        :return:
        """
        credentials_kwargs = {
            "api_key": credentials["dashscope_api_key"],
        }

        return credentials_kwargs

    def _convert_one_message_to_text(self, message: PromptMessage) -> str:
        """
        Convert a single message to a string.

        :param message: PromptMessage to convert.
        :return: String representation of the message.
        """
        human_prompt = "\n\nHuman:"
        ai_prompt = "\n\nAssistant:"
        content = message.content

        if isinstance(message, UserPromptMessage):
            message_text = f"{human_prompt} {content}"
        elif isinstance(message, AssistantPromptMessage):
            message_text = f"{ai_prompt} {content}"
        elif isinstance(message, SystemPromptMessage):
            message_text = content
        else:
            raise ValueError(f"Got unknown type {message}")

        return message_text

    def _convert_messages_to_prompt(self, messages: List[PromptMessage]) -> str:
        """
        Format a list of messages into a full prompt for the Anthropic model

        :param messages: List of PromptMessage to combine.
        :return: Combined string with necessary human_prompt and ai_prompt tags.
        """
        messages = messages.copy()  # don't mutate the original list

        text = "".join(
            self._convert_one_message_to_text(message) for message in messages
        )

        # trim off the trailing ' ' that might come from the "Assistant: "
        return text.rstrip()

    def _convert_prompt_messages_to_tongyi_messages(
        self, prompt_messages: List[PromptMessage]
    ) -> List[dict]:
        """
        Convert prompt messages to tongyi messages

        :param prompt_messages: prompt messages
        :return: tongyi messages
        """
        tongyi_messages = []
        for prompt_message in prompt_messages:
            if isinstance(prompt_message, SystemPromptMessage):
                tongyi_messages.append(
                    {
                        "role": "system",
                        "content": prompt_message.content,
                    }
                )
            elif isinstance(prompt_message, UserPromptMessage):
                tongyi_messages.append(
                    {
                        "role": "user",
                        "content": prompt_message.content,
                    }
                )
            elif isinstance(prompt_message, AssistantPromptMessage):
                tongyi_messages.append(
                    {
                        "role": "assistant",
                        "content": prompt_message.content,
                    }
                )
            else:
                raise ValueError(f"Got unknown type {prompt_message}")

        return tongyi_messages

    @property
    def _invoke_error_mapping(self) -> Dict[Type[InvokeError], List[Type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the error type thrown to the caller
        The value is the error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke error mapping
        """
        return {
            InvokeConnectionError: [
                RequestFailure,
            ],
            InvokeServerUnavailableError: [
                ServiceUnavailableError,
            ],
            InvokeRateLimitError: [],
            InvokeAuthorizationError: [
                AuthenticationError,
            ],
            InvokeBadRequestError: [
                InvalidParameter,
                UnsupportedModel,
                UnsupportedHTTPMethod,
            ],
        }

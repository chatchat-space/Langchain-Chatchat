import json
import logging
from typing import Dict, Generator, List, Optional, Type, Union

import google.api_core.exceptions as exceptions
import google.generativeai as genai
import google.generativeai.client as client
from google.ai.generativelanguage_v1beta import FunctionCall, FunctionResponse
from google.generativeai.types import (
    ContentType,
    GenerateContentResponse,
    HarmBlockThreshold,
    HarmCategory,
)
from google.generativeai.types.content_types import (
    FunctionDeclaration,
    FunctionLibrary,
    Tool,
    to_part,
)

from model_providers.core.model_runtime.entities.llm_entities import (
    LLMResult,
    LLMResultChunk,
    LLMResultChunkDelta,
)
from model_providers.core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    PromptMessage,
    PromptMessageContentType,
    PromptMessageRole,
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

logger = logging.getLogger(__name__)

GEMINI_BLOCK_MODE_PROMPT = """You should always follow the instructions and output a valid {{block}} object.
The structure of the {{block}} object you can found in the instructions, use {"answer": "$your_answer"} as the default structure
if you are not sure about the structure.

<instructions>
{{instructions}}
</instructions>
"""


class GoogleLargeLanguageModel(LargeLanguageModel):
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
            model,
            credentials,
            prompt_messages,
            model_parameters,
            tools,
            stop,
            stream,
            user,
        )

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
        :return:md = genai.GenerativeModel(model)
        """
        prompt = self._convert_messages_to_prompt(prompt_messages)

        return self._get_num_tokens_by_gpt2(prompt)

    def _convert_messages_to_prompt(self, messages: List[PromptMessage]) -> str:
        """
        Format a list of messages into a full prompt for the Google model

        :param messages: List of PromptMessage to combine.
        :return: Combined string with necessary human_prompt and ai_prompt tags.
        """
        messages = messages.copy()  # don't mutate the original list

        text = "".join(
            self._convert_one_message_to_text(message) for message in messages
        )

        return text.rstrip()

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """

        try:
            ping_message = PromptMessage(content="ping", role="system")
            self._generate(
                model, credentials, [ping_message], {"max_tokens_to_sample": 5}
            )

        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    def _generate(
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
        :param credentials: credentials kwargs
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        config_kwargs = model_parameters.copy()
        config_kwargs.pop("max_tokens_to_sample", None)
        # https://github.com/google/generative-ai-python/issues/170
        # config_kwargs["max_output_tokens"] = config_kwargs.pop(
        #     "max_tokens_to_sample", None
        # )

        if stop:
            config_kwargs["stop_sequences"] = stop

        google_model = genai.GenerativeModel(model_name=model)

        history = []

        # hack for gemini-pro-vision, which currently does not support multi-turn chat
        if model == "gemini-pro-vision":
            last_msg = prompt_messages[-1]
            content = self._format_message_to_glm_content(last_msg)
            history.append(content)
        else:
            for msg in prompt_messages:  # makes message roles strictly alternating
                content = self._format_message_to_glm_content(msg)
                if history and history[-1]["role"] == content["role"]:
                    history[-1]["parts"].extend(content["parts"])
                else:
                    history.append(content)

        # Create a new ClientManager with tenant's API key
        new_client_manager = client._ClientManager()
        new_client_manager.configure(api_key=credentials["google_api_key"])
        new_custom_client = new_client_manager.make_client("generative")

        google_model._client = new_custom_client

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        tools_one = []
        for tool in tools:
            one_tool = Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters,
                    )
                ]
            )
            tools_one.append(one_tool)

        response = google_model.generate_content(
            contents=history,
            generation_config=genai.types.GenerationConfig(**config_kwargs),
            stream=stream,
            safety_settings=safety_settings,
            tools=FunctionLibrary(tools=tools_one),
        )

        if stream:
            return self._handle_generate_stream_response(
                model, credentials, response, prompt_messages
            )

        return self._handle_generate_response(
            model, credentials, response, prompt_messages
        )

    def _handle_generate_response(
        self,
        model: str,
        credentials: dict,
        response: GenerateContentResponse,
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
        part = response.candidates[0].content.parts[0]
        part_message_function_call = part.function_call
        tool_calls = []
        if part_message_function_call:
            function_call = self._extract_response_function_call(
                part_message_function_call
            )
            tool_calls.append(function_call)
        part_message_function_response = part.function_response
        if part_message_function_response:
            function_call = self._extract_response_function_call(
                part_message_function_call
            )
            tool_calls.append(function_call)

        # transform assistant message to prompt message
        assistant_prompt_message = AssistantPromptMessage(
            content=part.text, tool_calls=tool_calls
        )

        # calculate num tokens
        prompt_tokens = self.get_num_tokens(model, credentials, prompt_messages)
        completion_tokens = self.get_num_tokens(
            model, credentials, [assistant_prompt_message]
        )

        # transform usage
        usage = self._calc_response_usage(
            model, credentials, prompt_tokens, completion_tokens
        )

        # transform response
        result = LLMResult(
            model=model,
            prompt_messages=prompt_messages,
            message=assistant_prompt_message,
            usage=usage,
        )

        return result

    def _handle_generate_stream_response(
        self,
        model: str,
        credentials: dict,
        response: GenerateContentResponse,
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
        index = -1
        for chunk in response:
            content = chunk.text
            index += 1

            assistant_prompt_message = AssistantPromptMessage(
                content=content if content else "",
            )

            if not response._done:
                # transform assistant message to prompt message
                yield LLMResultChunk(
                    model=model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(
                        index=index, message=assistant_prompt_message
                    ),
                )
            else:
                # calculate num tokens
                prompt_tokens = self.get_num_tokens(model, credentials, prompt_messages)
                completion_tokens = self.get_num_tokens(
                    model, credentials, [assistant_prompt_message]
                )

                # transform usage
                usage = self._calc_response_usage(
                    model, credentials, prompt_tokens, completion_tokens
                )

                yield LLMResultChunk(
                    model=model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(
                        index=index,
                        message=assistant_prompt_message,
                        finish_reason=chunk.candidates[0].finish_reason,
                        usage=usage,
                    ),
                )

    def _convert_one_message_to_text(self, message: PromptMessage) -> str:
        """
        Convert a single message to a string.

        :param message: PromptMessage to convert.
        :return: String representation of the message.
        """
        human_prompt = "\n\nuser:"
        ai_prompt = "\n\nmodel:"

        content = message.content
        if isinstance(content, list):
            content = "".join(
                c.data for c in content if c.type != PromptMessageContentType.IMAGE
            )

        if isinstance(message, UserPromptMessage):
            message_text = f"{human_prompt} {content}"
        elif isinstance(message, AssistantPromptMessage):
            message_text = f"{ai_prompt} {content}"
        elif isinstance(message, SystemPromptMessage):
            message_text = f"{human_prompt} {content}"
        else:
            raise ValueError(f"Got unknown type {message}")

        return message_text

    def _format_message_to_glm_content(self, message: PromptMessage) -> ContentType:
        """
        Format a single message into glm.Content for Google API

        :param message: one PromptMessage
        :return: glm Content representation of message
        """

        parts = []
        if isinstance(message.content, str):
            parts.append(to_part(message.content))
        else:
            for c in message.content:
                if c.type == PromptMessageContentType.TEXT:
                    parts.append(to_part(c.data))
                else:
                    metadata, data = c.data.split(",", 1)
                    mime_type = metadata.split(";", 1)[0].split(":")[1]
                    blob = {"inline_data": {"mime_type": mime_type, "data": data}}
                    parts.append(blob)

        glm_content = {
            "role": "user"
            if message.role in (PromptMessageRole.USER, PromptMessageRole.SYSTEM)
            else "model",
            "parts": parts,
        }

        return glm_content

    @property
    def _invoke_error_mapping(self) -> Dict[Type[InvokeError], List[Type[Exception]]]:
        """
        Map model invoke error to unified error
        The key is the ermd = genai.GenerativeModel(model)ror type thrown to the caller
        The value is the md = genai.GenerativeModel(model)error type thrown by the model,
        which needs to be converted into a unified error type for the caller.

        :return: Invoke emd = genai.GenerativeModel(model)rror mapping
        """
        return {
            InvokeConnectionError: [exceptions.RetryError],
            InvokeServerUnavailableError: [
                exceptions.ServiceUnavailable,
                exceptions.InternalServerError,
                exceptions.BadGateway,
                exceptions.GatewayTimeout,
                exceptions.DeadlineExceeded,
            ],
            InvokeRateLimitError: [
                exceptions.ResourceExhausted,
                exceptions.TooManyRequests,
            ],
            InvokeAuthorizationError: [
                exceptions.Unauthenticated,
                exceptions.PermissionDenied,
                exceptions.Unauthenticated,
                exceptions.Forbidden,
            ],
            InvokeBadRequestError: [
                exceptions.BadRequest,
                exceptions.InvalidArgument,
                exceptions.FailedPrecondition,
                exceptions.OutOfRange,
                exceptions.NotFound,
                exceptions.MethodNotAllowed,
                exceptions.Conflict,
                exceptions.AlreadyExists,
                exceptions.Aborted,
                exceptions.LengthRequired,
                exceptions.PreconditionFailed,
                exceptions.RequestRangeNotSatisfiable,
                exceptions.Cancelled,
            ],
        }

    def _extract_response_function_call(
        self, response_function_call: Union[FunctionCall, FunctionResponse]
    ) -> AssistantPromptMessage.ToolCall:
        """
        Extract function call from response

        :param response_function_call: response function call
        :return: tool call
        """
        tool_call = None
        if response_function_call:
            if isinstance(response_function_call, FunctionCall):
                map_composite_dict = dict(response_function_call.args.items())
                function = AssistantPromptMessage.ToolCall.ToolCallFunction(
                    name=response_function_call.name,
                    arguments=str(map_composite_dict),
                )
            elif isinstance(response_function_call, FunctionResponse):
                map_composite_dict = dict(response_function_call.response.items())
                function = AssistantPromptMessage.ToolCall.ToolCallFunction(
                    name=response_function_call.name,
                    arguments=str(map_composite_dict),
                )
            else:
                raise ValueError(
                    f"Unsupported response_function_call type: {type(response_function_call)}"
                )

            tool_call = AssistantPromptMessage.ToolCall(
                id=response_function_call.name, type="function", function=function
            )

        return tool_call

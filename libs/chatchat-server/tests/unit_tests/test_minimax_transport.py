"""Exercise configured chat clients through the real SDK with offline HTTP."""

import json

import httpx
import pytest
from langchain_core.load import dumps, loads
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration

from chatchat.server import utils
from chatchat.settings import ApiModelSettings, PlatformConfig, Settings
from langchain_chatchat.agents.format_scratchpad.all_tools import (
    format_to_platform_tool_messages,
)
from langchain_chatchat.agents.output_parsers.platform_tools import (
    PlatformToolsAgentOutputParser,
)
from langchain_chatchat.chat_models import ChatPlatformAI

TOOL = {
    "type": "function",
    "function": {"name": "lookup", "parameters": {"type": "object", "properties": {}}},
}
TOOL_CALL = {
    "id": "call_test",
    "type": "function",
    "function": {"name": "lookup", "arguments": "{}"},
}
CONTENT = [
    {"type": "text", "text": "Describe this image."},
    {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}},
]


@pytest.fixture(autouse=True)
def disable_settings_reload(monkeypatch):
    monkeypatch.setattr(Settings.model_settings, "auto_reload", False)


@pytest.fixture(params=["minimax-global", "minimax-cn"])
def platform(request, monkeypatch):
    platform = next(
        p.model_copy(deep=True)
        for p in ApiModelSettings.model_fields["MODEL_PLATFORMS"].default
        if p.platform_name == request.param
    )
    platform.api_key = "test"
    monkeypatch.setattr(Settings.model_settings, "MODEL_PLATFORMS", [platform])
    return platform


def transport(requests, stream=False, asynchronous=False):
    def respond(request):
        requests.append((str(request.url), json.loads(request.content)))
        message = {
            "role": "assistant",
            "content": "<think>Keep this.</think>",
            "reasoning_content": "Keep this reasoning too.",
            "tool_calls": [TOOL_CALL],
        }
        response = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": requests[-1][1]["model"],
            "choices": [
                {"index": 0, "message": message, "finish_reason": "tool_calls"}
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
        if stream:
            message["tool_calls"] = [{"index": 0, **TOOL_CALL}]
            response["object"] = "chat.completion.chunk"
            message["reasoning_content"] = "reasoning too."
            response["choices"] = [
                {"index": 0, "delta": message, "finish_reason": "tool_calls"}
            ]
            prefix = {
                **response,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": None,
                        "delta": {
                            "role": "assistant",
                            "reasoning_content": "Keep this ",
                        },
                    }
                ],
            }
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                text=(
                    f"data: {json.dumps(prefix)}\n\n"
                    f"data: {json.dumps(response)}\n\ndata: [DONE]\n\n"
                ),
            )
        return httpx.Response(200, json=response)

    client = httpx.AsyncClient if asynchronous else httpx.Client
    return client(transport=httpx.MockTransport(respond))


@pytest.mark.parametrize("effort", [None, "low", "medium", "high", "xhigh", "max"])
@pytest.mark.parametrize("stream", [False, True])
def test_agent_sdk_history_and_effort(platform, effort, stream):
    requests = []
    assert utils.get_default_llm() == "MiniMax-M3.1-Flash"
    params = utils.get_ChatPlatformAIParams(
        model_name=utils.get_default_llm(),
        streaming=stream,
        http_client=transport(requests, stream),
    )
    llm = ChatPlatformAI(**params)
    kwargs = {"tools": [TOOL]}
    if effort:
        kwargs["reasoning_effort"] = effort
    user = HumanMessage(content=CONTENT)
    reply = llm.invoke([user], **kwargs)
    assert reply.additional_kwargs["reasoning_content"] == "Keep this reasoning too."
    actions = PlatformToolsAgentOutputParser(
        instance_type="platform-knowledge-mode"
    ).parse_result([ChatGeneration(message=reply)])
    steps = loads(dumps([(actions[0], "Found.")]))
    scratchpad = format_to_platform_tool_messages(steps)
    llm.invoke([user, *scratchpad])
    url, payload = requests[0]
    assert url == platform.api_base_url + "/chat/completions"
    assert payload["model"] == "MiniMax-M3.1-Flash"
    assert payload.get("reasoning_effort") == effort
    assert payload["tools"] == [TOOL]
    assert payload["messages"][0]["content"] == CONTENT
    assert "service_tier" not in payload
    assert "thinking" not in payload  # The API defaults to adaptive thinking.
    history = requests[1][1]["messages"]
    assert history[1]["reasoning_content"] == "Keep this reasoning too."
    assert history[1]["content"] == "<think>Keep this.</think>"
    assert history[1]["tool_calls"][0]["id"] == "call_test"
    assert history[2]["tool_call_id"] == "call_test"


@pytest.mark.parametrize("model", ["MiniMax-M3", "MiniMax-M2.7", "saved-custom-id"])
def test_saved_models_are_not_replaced(platform, monkeypatch, model):
    platform.llm_models = [model]
    monkeypatch.setattr(Settings.model_settings, "DEFAULT_LLM_MODEL", model)
    assert utils.get_default_llm() == model
    assert list(utils.get_config_models(model_type="llm")) == [model]
    requests = []
    llm = ChatPlatformAI(
        **utils.get_ChatPlatformAIParams(
            model_name=model,
            streaming=False,
            http_client=transport(requests),
        )
    )
    llm.invoke([HumanMessage(content=CONTENT)])
    assert requests[0][1]["model"] == model
    assert requests[0][1]["messages"][0]["content"] == CONTENT


@pytest.mark.parametrize("stream", [False, True])
def test_chat_factory_sdk_payload(platform, stream):
    import openai

    requests = []
    client = openai.OpenAI(
        api_key="test",
        base_url=platform.api_base_url,
        http_client=transport(requests, stream),
    )
    llm = utils.get_ChatOpenAI(
        model_name=platform.llm_models[0],
        streaming=stream,
        client=client.chat.completions,
    )
    assert llm is not None
    user = HumanMessage(content=CONTENT)
    reply = llm.invoke([user], reasoning_effort="high", tools=[TOOL])
    llm.invoke([user, reply, ToolMessage(content="Found.", tool_call_id="call_test")])
    assert requests[1][1]["messages"][1]["reasoning_content"] == (
        "Keep this reasoning too."
    )
    url, payload = requests[0]
    assert url == platform.api_base_url + "/chat/completions"
    assert payload["model"] == "MiniMax-M3.1-Flash"
    assert payload["reasoning_effort"] == "high"
    assert payload["messages"][0]["content"] == CONTENT
    client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True])
async def test_async_chat_factory_sdk_history(platform, stream):
    import openai

    requests = []
    client = openai.AsyncOpenAI(
        api_key="test",
        base_url=platform.api_base_url,
        http_client=transport(requests, stream, asynchronous=True),
    )
    llm = utils.get_ChatOpenAI(
        model_name=platform.llm_models[0],
        streaming=stream,
        async_client=client.chat.completions,
        http_client=transport([], stream),
    )
    user = HumanMessage(content=CONTENT)
    reply = await llm.ainvoke([user], reasoning_effort="max", tools=[TOOL])
    await llm.ainvoke(
        [user, reply, ToolMessage(content="Found.", tool_call_id="call_test")]
    )
    assert requests[0][1]["reasoning_effort"] == "max"
    assert requests[0][1]["messages"][0]["content"] == CONTENT
    assert requests[1][1]["messages"][1]["reasoning_content"] == (
        "Keep this reasoning too."
    )
    await client.close()


def test_non_minimax_and_media_settings_are_preserved(monkeypatch):
    platform = PlatformConfig(
        platform_name="saved",
        platform_type="custom openai",
        api_base_url="https://example.com/v1",
        api_key="test",
        llm_models=["saved-model"],
        image2text_models=["saved-vision"],
        text2speech_models=["saved-speech"],
        embed_models=["saved-embedding"],
    )
    monkeypatch.setattr(Settings.model_settings, "MODEL_PLATFORMS", [platform])
    assert list(utils.get_config_models(model_type="llm")) == ["saved-model"]
    assert list(utils.get_config_models(model_type="image2text")) == ["saved-vision"]
    assert list(utils.get_config_models(model_type="text2speech")) == ["saved-speech"]
    assert list(utils.get_config_models(model_type="embed")) == ["saved-embedding"]
    requests = []
    llm = ChatPlatformAI(
        **utils.get_ChatPlatformAIParams(
            model_name="saved-model",
            streaming=False,
            http_client=transport(requests),
        )
    )
    llm.invoke([HumanMessage(content="Hello")])
    assert requests[0][0] == "https://example.com/v1/chat/completions"
    assert requests[0][1]["model"] == "saved-model"
    assert "reasoning_effort" not in requests[0][1]


@pytest.mark.asyncio
@pytest.mark.parametrize("platform_type", ["minimax", "openai"])
async def test_discovered_models_keep_saved_and_media(
    platform, monkeypatch, platform_type
):
    import openai

    from chatchat.server.api_server import openai_routes

    platform.platform_type = platform_type
    platform.llm_models.append("MiniMax-M2.7")
    ids = [
        "MiniMax-M2.5",
        "MiniMax-M3",
        "MiniMax-M2.7",
        "saved-custom-id",
        "image-01",
        "speech-02-hd",
        "MiniMax-VL-01",
        "MiniMax-M3.1-Flash",
        "abab6.5s-chat",
        "MiniMax-Text-01",
    ]

    def respond(request):
        assert str(request.url) == platform.api_base_url + "/models"
        return httpx.Response(
            200,
            json={
                "object": "list",
                "data": [
                    {"id": model, "object": "model", "created": 0, "owned_by": "test"}
                    for model in ids
                ],
            },
        )

    client = openai.AsyncOpenAI(
        api_key="test",
        base_url=platform.api_base_url,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
    )
    monkeypatch.setattr(openai_routes, "get_OpenAIClient", lambda *a, **kw: client)
    response = await openai_routes.list_models()
    expected = (
        [
            "MiniMax-M3.1-Flash",
            "MiniMax-M3",
            "MiniMax-M2.7",
            "saved-custom-id",
            "image-01",
            "speech-02-hd",
            "MiniMax-VL-01",
        ]
        if platform_type == "minimax"
        else ids
    )
    assert [item["id"] for item in response["data"]] == expected
    await client.close()


@pytest.mark.asyncio
async def test_local_proxy_preserves_reasoning_history(platform, monkeypatch):
    import openai

    from chatchat.server.api_server import openai_routes
    from chatchat.server.api_server.api_schemas import OpenAIChatInput

    requests = []
    client = openai.AsyncOpenAI(
        api_key="test",
        base_url=platform.api_base_url,
        http_client=transport(requests, asynchronous=True),
    )
    monkeypatch.setattr(openai_routes, "get_OpenAIClient", lambda **kw: client)
    messages = [
        {"role": "user", "content": CONTENT},
        {
            "role": "assistant",
            "content": "<think>Keep this.</think>",
            "reasoning_content": "Keep this reasoning too.",
            "tool_calls": [TOOL_CALL],
        },
        {"role": "tool", "content": "Found.", "tool_call_id": "call_test"},
    ]
    body = OpenAIChatInput(
        model=platform.llm_models[0],
        messages=messages,
        reasoning_effort="high",
    )
    await openai_routes.create_chat_completions(body)
    assert requests[0][1]["messages"] == messages
    assert requests[0][1]["reasoning_effort"] == "high"
    body = OpenAIChatInput(
        model="MiniMax-M3",
        messages=messages,
        extra_body={"thinking": {"type": "disabled"}},
    )
    await openai_routes.create_chat_completions(body)
    assert requests[1][1]["thinking"] == {"type": "disabled"}
    assert "extra_json" not in requests[1][1]
    await client.close()


def test_m3_can_disable_thinking(platform):
    requests = []
    llm = ChatPlatformAI(
        **utils.get_ChatPlatformAIParams(
            model_name="MiniMax-M3",
            streaming=False,
            http_client=transport(requests),
        )
    )
    user = HumanMessage(content="Hello")
    reply = llm.invoke(
        [user],
        extra_body={"thinking": {"type": "disabled"}},
    )
    assert requests[0][1]["thinking"] == {"type": "disabled"}
    assert requests[0][1]["model"] == "MiniMax-M3"
    reply.additional_kwargs.pop("reasoning_content")
    actions = PlatformToolsAgentOutputParser(
        instance_type="platform-knowledge-mode"
    ).parse_result([ChatGeneration(message=reply)])
    steps = loads(dumps([(actions[0], "Found.")]))
    scratchpad = format_to_platform_tool_messages(steps)
    llm.invoke([user, *scratchpad])
    assert requests[1][1]["messages"][1]["content"] == "<think>Keep this.</think>"

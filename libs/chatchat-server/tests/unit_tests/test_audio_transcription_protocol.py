from email import policy
from email.parser import BytesParser

import httpx
import pytest
from fastapi import FastAPI
from openai import AsyncOpenAI

from chatchat.server.api_server import openai_routes


@pytest.fixture
async def transcription_gateway(monkeypatch):
    requests = []
    responses = []

    async def upstream_handler(request):
        message = BytesParser(policy=policy.default).parsebytes(
            b"Content-Type: "
            + request.headers["content-type"].encode()
            + b"\r\n\r\n"
            + await request.aread()
        )
        fields = {}
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            fields.setdefault(name, []).append(part.get_payload(decode=True))
        requests.append(fields)
        return responses.pop(0)

    async with AsyncOpenAI(
        base_url="http://upstream.test/v1",
        api_key="EMPTY",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(upstream_handler)),
    ) as upstream:
        monkeypatch.setattr(openai_routes, "model_semaphores", {})
        monkeypatch.setattr(
            openai_routes,
            "get_model_info",
            lambda **kwargs: {"sensevoice": {"platform_name": "funasr"}},
        )
        monkeypatch.setattr(
            openai_routes, "get_OpenAIClient", lambda **kwargs: upstream
        )
        app = FastAPI()
        app.include_router(openai_routes.openai_router)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://gateway.test/v1/",
        ) as http_client:
            async with AsyncOpenAI(
                base_url="http://gateway.test/v1",
                api_key="EMPTY",
                max_retries=0,
                http_client=http_client,
            ) as client:
                yield client, http_client, requests, responses


@pytest.mark.parametrize(
    "response_format,media_type,body",
    [
        ("text", "text/plain", "Hello, world!\n"),
        (
            "srt",
            "application/x-subrip",
            "1\n00:00:00,000 --> 00:00:01,000\nHello, world!\n\n",
        ),
        (
            "vtt",
            "text/vtt",
            "WEBVTT\n\n00:00.000 --> 00:01.000\nHello, world!\n\n",
        ),
    ],
)
async def test_sdk_transcription_preserves_text_responses(
    transcription_gateway, response_format, media_type, body
):
    client, _, requests, responses = transcription_gateway
    responses.append(httpx.Response(200, text=body))
    response = await client.audio.transcriptions.with_raw_response.create(
        model="sensevoice",
        file=("sample.wav", b"RIFFaudio", "audio/wav"),
        response_format=response_format,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].split(";")[0] == media_type
    assert response.parse() == body
    assert requests[0]["response_format"] == [response_format.encode()]
    assert requests[0]["file"] == [b"RIFFaudio"]


@pytest.mark.parametrize("response_format", [None, "json", "verbose_json"])
async def test_sdk_transcription_preserves_json_responses(
    transcription_gateway, response_format
):
    client, _, requests, responses = transcription_gateway
    payload = {"text": "Hello, world!"}
    if response_format == "verbose_json":
        payload.update(
            task="transcribe",
            language="english",
            duration=1.0,
            words=[{"word": "Hello,", "start": 0.0, "end": 0.5}],
            segments=[],
        )
    responses.append(httpx.Response(200, json=payload))
    options = {} if response_format is None else {"response_format": response_format}
    response = await client.audio.transcriptions.with_raw_response.create(
        model="sensevoice",
        file=("sample.wav", b"RIFFaudio", "audio/wav"),
        **options,
    )
    assert response.headers["content-type"] == "application/json"
    assert response.parse().model_dump(exclude_none=True) == payload
    if response_format is None:
        assert "response_format" not in requests[0]


@pytest.mark.parametrize("granularities", [["word"], ["segment"], ["word", "segment"]])
async def test_sdk_transcription_forwards_timestamp_granularities(
    transcription_gateway, granularities
):
    client, _, requests, responses = transcription_gateway
    responses.append(
        httpx.Response(
            200,
            json={
                "text": "Hello!",
                "task": "transcribe",
                "language": "english",
                "duration": 1.0,
                "words": [],
                "segments": [],
            },
        )
    )
    result = await client.audio.transcriptions.create(
        model="sensevoice",
        file=("sample.wav", b"RIFFaudio", "audio/wav"),
        response_format="verbose_json",
        timestamp_granularities=granularities,
    )
    assert result.text == "Hello!"
    assert requests[0].get("timestamp_granularities[]") == [
        value.encode() for value in granularities
    ]


@pytest.mark.parametrize("standard", [None, ["segment"]])
async def test_timestamp_fields_preserve_legacy_and_prefer_standard(
    transcription_gateway, standard
):
    _, http_client, requests, responses = transcription_gateway
    responses.append(httpx.Response(200, json={"text": "Hello!"}))
    data = {"model": "sensevoice", "timestamp_granularities": ["word"]}
    if standard is not None:
        data["timestamp_granularities[]"] = standard
    response = await http_client.post(
        "audio/transcriptions",
        data=data,
        files={"file": ("sample.wav", b"RIFFaudio", "audio/wav")},
    )
    assert response.status_code == 200
    assert response.json() == {"text": "Hello!"}
    expected = [b"word"] if standard is None else [b"segment"]
    assert requests[0].get("timestamp_granularities[]") == expected

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from openai import AsyncOpenAI

from chatchat.server.api_server import openai_routes
from chatchat.settings import Settings


class FakeTranscription:
    def model_dump(self, **kwargs):
        return {"text": "你好，世界"}


class FakeTranscriptions:
    def __init__(self):
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeTranscription()


def test_audio_transcription_proxies_openai_multipart_request(monkeypatch):
    transcriptions = FakeTranscriptions()
    client = type(
        "FakeOpenAIClient",
        (),
        {"audio": type("Audio", (), {"transcriptions": transcriptions})()},
    )()

    @asynccontextmanager
    async def fake_get_model_client(model_name):
        assert model_name == "sensevoice"
        yield client

    monkeypatch.setattr(openai_routes, "get_model_client", fake_get_model_client)

    app = FastAPI()
    app.include_router(openai_routes.openai_router)
    response = TestClient(app).post(
        "/v1/audio/transcriptions",
        data={
            "model": "sensevoice",
            "language": "zh",
            "prompt": "FunASR",
            "response_format": "json",
            "temperature": "0",
        },
        files={"file": ("sample.wav", b"RIFFaudio", "audio/wav")},
    )

    assert response.status_code == 200
    assert response.json() == {"text": "你好，世界"}
    assert transcriptions.calls == [
        {
            "file": ("sample.wav", b"RIFFaudio", "audio/wav"),
            "model": "sensevoice",
            "language": "zh",
            "prompt": "FunASR",
            "response_format": "json",
            "temperature": 0.0,
        }
    ]


def test_default_settings_include_local_funasr_platform():
    platforms = {
        platform.platform_name: platform
        for platform in Settings.model_settings.MODEL_PLATFORMS
    }

    funasr = platforms["funasr"]
    assert funasr.platform_type == "custom openai"
    assert funasr.api_base_url == "http://127.0.0.1:8000/v1"
    assert funasr.api_key == "EMPTY"
    assert funasr.speech2text_models == [
        "sensevoice",
        "paraformer",
        "paraformer-en",
        "fun-asr-nano",
    ]


def test_audio_transcription_uses_real_openai_multipart_wire_format(monkeypatch):
    upstream_requests = []

    async def upstream_handler(request):
        upstream_requests.append(
            {
                "path": request.url.path,
                "content_type": request.headers["content-type"],
                "body": await request.aread(),
            }
        )
        return httpx.Response(200, json={"text": "真实协议转写"})

    @asynccontextmanager
    async def fake_get_model_client(model_name):
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(upstream_handler)
        ) as http_client:
            yield AsyncOpenAI(
                base_url="http://funasr.test/v1",
                api_key="EMPTY",
                http_client=http_client,
            )

    monkeypatch.setattr(openai_routes, "get_model_client", fake_get_model_client)

    app = FastAPI()
    app.include_router(openai_routes.openai_router)
    response = TestClient(app).post(
        "/v1/audio/transcriptions",
        data={"model": "sensevoice", "language": "zh"},
        files={"file": ("sample.wav", b"RIFFaudio", "audio/wav")},
    )

    assert response.status_code == 200
    assert response.json() == {"text": "真实协议转写"}
    assert len(upstream_requests) == 1
    request = upstream_requests[0]
    assert request["path"] == "/v1/audio/transcriptions"
    assert request["content_type"].startswith("multipart/form-data; boundary=")
    assert b'name="model"' in request["body"]
    assert b"sensevoice" in request["body"]
    assert b'name="language"' in request["body"]
    assert b'name="file"; filename="sample.wav"' in request["body"]
    assert b"RIFFaudio" in request["body"]

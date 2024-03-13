from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Tuple, AsyncGenerator

from fastapi import APIRouter, Request
from openai import AsyncClient
from sse_starlette.sse import EventSourceResponse

from .api_schemas import *
from configs import logger
from server.utils import get_model_info, get_config_platforms, get_OpenAIClient


DEFAULT_API_CONCURRENCIES = 5 # 默认单个模型最大并发数
model_semaphores: Dict[Tuple[str, str], asyncio.Semaphore] = {} # key: (model_name, platform)
openai_router = APIRouter(prefix="/v1", tags=["OpenAI 兼容平台整合接口"])


@asynccontextmanager
async def acquire_model_client(model_name: str) -> AsyncGenerator[AsyncClient]:
    '''
    对重名模型进行调度，依次选择：空闲的模型 -> 当前访问数最少的模型
    '''
    max_semaphore = 0
    selected_platform = ""
    model_infos = get_model_info(model_name=model_name, multiple=True)
    for m, c in model_infos.items():
        key = (m, c["platform_name"])
        api_concurrencies = c.get("api_concurrencies", DEFAULT_API_CONCURRENCIES)
        if key not in model_semaphores:
            model_semaphores[key] = asyncio.Semaphore(api_concurrencies)
        semaphore = model_semaphores[key]
        if semaphore._value >= api_concurrencies:
            selected_platform = c["platform_name"]
            break
        elif semaphore._value > max_semaphore:
            selected_platform = c["platform_name"]

    key = (m, selected_platform)
    semaphore = model_semaphores[key]
    try:
        await semaphore.acquire()
        yield get_OpenAIClient(platform_name=selected_platform, is_async=True)
    except Exception:
        logger.error(f"failed when request to {key}", exc_info=True)
    finally:
        semaphore.release()


async def openai_request(method, body):
    '''
    helper function to make openai request
    '''
    async def generator():
        async for chunk in await method(**params):
            yield {"data": chunk.json()}

    params = body.dict(exclude_unset=True)
    if hasattr(body, "stream") and body.stream:
        return EventSourceResponse(generator())
    else:
        return (await method(**params)).dict()


@openai_router.get("/models")
async def list_models() -> List:
    '''
    整合所有平台的模型列表。
    '''
    async def task(name: str, config: Dict):
        try:
            client = get_OpenAIClient(name, is_async=True)
            models = await client.models.list()
            if config.get("platform_type") == "xinference":
                models = models.dict(exclude={"data":..., "object":...})
                for x in models:
                    models[x]["platform_name"] = name
                return [{**v, "id": k} for k, v in models.items()]
            elif config.get("platform_type") == "oneapi":
                return [{**x.dict(), "platform_name": name} for x in models.data]
        except Exception:
            logger.error(f"failed request to platform: {name}", exc_info=True)
            return {}

    result = []
    tasks = [asyncio.create_task(task(name, config)) for name, config in get_config_platforms().items()]
    for t in asyncio.as_completed(tasks):
        result += (await t)
    return result


@openai_router.post("/chat/completions")
async def create_chat_completions(
    request: Request,
    body: OpenAIChatInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.chat.completions.create, body)


@openai_router.post("/completions")
async def create_completions(
    request: Request,
    body: OpenAIChatInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.completions.create, body)


@openai_router.post("/embeddings")
async def create_embeddings(
    request: Request,
    body: OpenAIEmbeddingsInput,
):
    params = body.dict(exclude_unset=True)
    client = get_OpenAIClient(model_name=body.model)
    return (await client.embeddings.create(**params)).dict()


@openai_router.post("/images/generations")
async def create_image_generations(
    request: Request,
    body: OpenAIImageGenerationsInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.images.generate, body)


@openai_router.post("/images/variations")
async def create_image_variations(
    request: Request,
    body: OpenAIImageVariationsInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.images.create_variation, body)


@openai_router.post("/images/edit")
async def create_image_edit(
    request: Request,
    body: OpenAIImageEditsInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.images.edit, body)

    
@openai_router.post("/audio/translations", deprecated="暂不支持")
async def create_audio_translations(
    request: Request,
    body: OpenAIAudioTranslationsInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.audio.translations.create, body)


@openai_router.post("/audio/transcriptions", deprecated="暂不支持")
async def create_audio_transcriptions(
    request: Request,
    body: OpenAIAudioTranscriptionsInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.audio.transcriptions.create, body)


@openai_router.post("/audio/speech", deprecated="暂不支持")
async def create_audio_speech(
    request: Request,
    body: OpenAIAudioSpeechInput,
):
    async with acquire_model_client(body.model) as client:
        return await openai_request(client.audio.speech.create, body)


@openai_router.post("/files", deprecated="暂不支持")
async def files():
    ...

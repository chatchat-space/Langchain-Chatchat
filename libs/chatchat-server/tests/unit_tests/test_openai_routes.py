import asyncio

import pytest

from chatchat.server.api_server import openai_routes


@pytest.fixture(autouse=True)
def clear_model_semaphores():
    openai_routes.model_semaphores.clear()
    yield
    openai_routes.model_semaphores.clear()


@pytest.mark.asyncio
async def test_get_model_client_waits_when_all_slots_are_busy(monkeypatch):
    model_name = "test-model"
    platform_name = "test-platform"
    key = (model_name, platform_name)
    expected_client = object()

    semaphore = asyncio.Semaphore(0)
    openai_routes.model_semaphores[key] = semaphore

    monkeypatch.setattr(
        openai_routes,
        "get_model_info",
        lambda model_name, multiple: {
            model_name: {
                "platform_name": platform_name,
                "api_concurrencies": 1,
            }
        },
    )
    monkeypatch.setattr(
        openai_routes,
        "get_OpenAIClient",
        lambda **kwargs: expected_client,
    )

    async def acquire_client():
        async with openai_routes.get_model_client(model_name) as client:
            return client

    task = asyncio.create_task(acquire_client())
    await asyncio.sleep(0)

    if task.done():
        task.result()

    assert not task.done()

    semaphore.release()

    assert await asyncio.wait_for(task, timeout=1) is expected_client

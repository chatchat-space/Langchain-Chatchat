import asyncio
import logging

import pytest

from model_providers import BootstrapWebBuilder

logger = logging.getLogger(__name__)


@pytest.mark.requires("fastapi")
def test_init_server(logging_conf: dict) -> None:
    try:
        boot = (
            BootstrapWebBuilder()
            .model_providers_cfg_path(
                model_providers_cfg_path="/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/model-providers"
                "/model_providers.yaml"
            )
            .host(host="127.0.0.1")
            .port(port=20000)
            .build()
        )
        boot.set_app_event(started_event=None)
        boot.serve(logging_conf=logging_conf)

        async def pool_join_thread():
            await boot.join()

        asyncio.run(pool_join_thread())
    except SystemExit:
        logger.info("SystemExit raised, exiting")
        raise

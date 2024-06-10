from typing import List, Dict
from chatchat.configs import MODEL_PROVIDERS_CFG_HOST, MODEL_PROVIDERS_CFG_PORT, MODEL_PROVIDERS_CFG_PATH_CONFIG
from model_providers import BootstrapWebBuilder
from model_providers.bootstrap_web.entities.model_provider_entities import ProviderResponse
from model_providers.core.bootstrap.providers_wapper import ProvidersWrapper
from model_providers.core.provider_manager import ProviderManager
from model_providers.core.utils.utils import (
    get_config_dict,
    get_log_file,
    get_timestamp_ms,
)
import multiprocessing as mp
import asyncio
import logging

logger = logging.getLogger(__name__)


def init_server(model_platforms_shard: Dict,
                started_event: mp.Event = None,
                model_providers_cfg_path: str = MODEL_PROVIDERS_CFG_PATH_CONFIG,
                provider_host: str = MODEL_PROVIDERS_CFG_HOST,
                provider_port: int = MODEL_PROVIDERS_CFG_PORT,
                log_path: str = "logs"
                ) -> None:
    logging_conf = get_config_dict(
        "INFO",
        get_log_file(log_path=log_path, sub_dir=f"provider_{get_timestamp_ms()}"),

        1024*1024*1024*3,
        1024*1024*1024*3,
    )

    try:
        boot = (
            BootstrapWebBuilder()
            .model_providers_cfg_path(
                model_providers_cfg_path=model_providers_cfg_path
            )
            .host(host=provider_host)
            .port(port=provider_port)
            .build()
        )
        boot.set_app_event(started_event=started_event)

        provider_platforms = init_provider_platforms(boot.provider_manager.provider_manager)
        model_platforms_shard['provider_platforms'] = provider_platforms
        boot.logging_conf(logging_conf=logging_conf)
        boot.run()

        async def pool_join_thread():
            await boot.join()

        asyncio.run(pool_join_thread())
    except SystemExit:
        logger.info("SystemExit raised, exiting")
        raise


def init_provider_platforms(provider_manager: ProviderManager)-> List[Dict]:
    provider_list: List[ProviderResponse] = ProvidersWrapper(
                        provider_manager=provider_manager).get_provider_list()
    logger.info(f"Provider list: {provider_list}")
    # 转换MODEL_PLATFORMS
    provider_platforms = []
    for provider in provider_list:
        provider_dict = {
            "platform_name": provider.provider,
            "platform_type": provider.provider,
            "api_base_url": f"http://127.0.0.1:20000/{provider.provider}/v1",
            "api_key": "EMPTY",
            "api_concurrencies": 5
        }

        provider_dict["llm_models"] = []
        provider_dict["embed_models"] = []
        provider_dict["image_models"] = []
        provider_dict["reranking_models"] = []
        provider_dict["speech2text_models"] = []
        provider_dict["tts_models"] = []
        supported_model_str_types = [model_type.to_origin_model_type() for model_type in
                                     provider.supported_model_types]

        for model_type in supported_model_str_types:

            providers_model_type = ProvidersWrapper(
                provider_manager=provider_manager
            ).get_models_by_model_type(model_type=model_type)
            cur_model_type: List[str] = []
            # 查询当前provider的模型
            for provider_model in providers_model_type:
                if provider_model.provider == provider.provider:
                    models = [model.model for model in provider_model.models]
                    cur_model_type.extend(models)

            if cur_model_type:
                if model_type == "text-generation":
                    provider_dict["llm_models"] = cur_model_type
                elif model_type == "embeddings":
                    provider_dict["embed_models"] = cur_model_type
                elif model_type == "text2img":
                    provider_dict["image_models"] = cur_model_type
                elif model_type == "reranking":
                    provider_dict["reranking_models"] = cur_model_type
                elif model_type == "speech2text":
                    provider_dict["speech2text_models"] = cur_model_type
                elif model_type == "tts":
                    provider_dict["tts_models"] = cur_model_type
                else:
                    logger.warning(f"Unsupported model type: {model_type}")

        provider_platforms.append(provider_dict)

    logger.info(f"Provider platforms: {provider_platforms}")

    return provider_platforms
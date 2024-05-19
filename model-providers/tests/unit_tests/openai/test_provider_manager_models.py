import asyncio
import logging

import pytest
from omegaconf import OmegaConf

from model_providers import BootstrapWebBuilder, _to_custom_provide_configuration
from model_providers.core.model_manager import ModelManager
from model_providers.core.model_runtime.entities.model_entities import ModelType
from model_providers.core.provider_manager import ProviderManager

logger = logging.getLogger(__name__)


def test_provider_manager_models(logging_conf: dict, providers_file: str) -> None:
    logging.config.dictConfig(logging_conf)  # type: ignore
    # 读取配置文件
    cfg = OmegaConf.load(
        providers_file
    )
    # 转换配置文件
    (
        provider_name_to_provider_records_dict,
        provider_name_to_provider_model_records_dict,
    ) = _to_custom_provide_configuration(cfg)
    # 创建模型管理器
    provider_manager = ProviderManager(
        provider_name_to_provider_records_dict=provider_name_to_provider_records_dict,
        provider_name_to_provider_model_records_dict=provider_name_to_provider_model_records_dict,
    )

    provider_model_bundle_llm = provider_manager.get_provider_model_bundle(
        provider="openai", model_type=ModelType.LLM
    )
    llm_models: List[AIModelEntity] = []
    for model in provider_model_bundle_llm.configuration.custom_configuration.models:

        llm_models.append(provider_model_bundle_llm.model_type_instance.get_model_schema(
            model=model.model,
            credentials=model.credentials,
        ))

    # 获取预定义模型
    llm_models.extend(
        provider_model_bundle_llm.model_type_instance.predefined_models()
    )

    logger.info(f"predefined_models: {llm_models}")

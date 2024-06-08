import asyncio
import logging

import pytest
from omegaconf import OmegaConf

from model_providers import BootstrapWebBuilder, _to_custom_provide_configuration
from model_providers.core.bootstrap.providers_wapper import ProvidersWrapper
from model_providers.core.model_manager import ModelManager
from model_providers.core.model_runtime.entities.model_entities import ModelType
from model_providers.core.provider_manager import ProviderManager

logger = logging.getLogger(__name__)


def test_provider_manager_models(logging_conf: dict, providers_file: str) -> None:
    logging.config.dictConfig(logging_conf)  # type: ignore
    # 读取配置文件
    cfg = OmegaConf.load(providers_file)
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

    ai_models: List[AIModelEntity] = []
    for model_type in ModelType.__members__.values():
        try:
            provider_model_bundle_llm = provider_manager.get_provider_model_bundle(
                provider="zhipuai", model_type=model_type
            )
            for (
                model
            ) in provider_model_bundle_llm.configuration.custom_configuration.models:
                if model.model_type == model_type:
                    ai_models.append(
                        provider_model_bundle_llm.model_type_instance.get_model_schema(
                            model=model.model,
                            credentials=model.credentials,
                        )
                    )
        except Exception as e:
            logger.warning("Error loading model: %s", e)

    # 获取预定义模型
    ai_models.extend(provider_model_bundle_llm.model_type_instance.predefined_models())

    logger.info(f"ai_models: {ai_models}")


def test_provider_wrapper_models(logging_conf: dict, providers_file: str) -> None:
    logging.config.dictConfig(logging_conf)  # type: ignore
    # 读取配置文件
    cfg = OmegaConf.load(providers_file)
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

    for model_type in ModelType.__members__.values():
        models_by_model_type = ProvidersWrapper(
            provider_manager=provider_manager
        ).get_models_by_model_type(model_type=model_type.to_origin_model_type())

        print(f"{model_type.to_origin_model_type()}:{models_by_model_type}")

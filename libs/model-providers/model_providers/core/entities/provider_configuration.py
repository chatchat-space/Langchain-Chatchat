import datetime
import json
import logging
from json import JSONDecodeError
from typing import Dict, Iterator, List, Optional

from model_providers.core.entities.model_entities import (
    ModelStatus,
    ModelWithProviderEntity,
    SimpleModelProviderEntity,
)
from model_providers.core.entities.provider_entities import CustomConfiguration
from model_providers.core.model_runtime.entities.model_entities import (
    FetchFrom,
    ModelType,
)
from model_providers.core.model_runtime.entities.provider_entities import (
    ConfigurateMethod,
    CredentialFormSchema,
    FormType,
    ProviderEntity,
)
from model_providers.core.model_runtime.model_providers import model_provider_factory
from model_providers.core.model_runtime.model_providers.__base.ai_model import AIModel
from model_providers.core.model_runtime.model_providers.__base.model_provider import (
    ModelProvider,
)

from ..._compat import PYDANTIC_V2, ConfigDict
from ..._models import BaseModel

logger = logging.getLogger(__name__)


class ProviderConfiguration(BaseModel):
    """
    Model class for provider configuration.
    """

    provider: ProviderEntity
    custom_configuration: CustomConfiguration

    def __init__(self, **data):
        super().__init__(**data)

    def get_current_credentials(
        self, model_type: ModelType, model: str
    ) -> Optional[dict]:
        """
        Get current credentials.

        :param model_type: model type
        :param model: model name
        :return:
        """
        if self.custom_configuration.models:
            for model_configuration in self.custom_configuration.models:
                if (
                    model_configuration.model_type == model_type
                    and model_configuration.model == model
                ):
                    return model_configuration.credentials

        if self.custom_configuration.provider:
            return self.custom_configuration.provider.credentials
        else:
            return None

    def is_custom_configuration_available(self) -> bool:
        """
        Check custom configuration available.
        :return:
        """
        return (
            self.custom_configuration.provider is not None
            or len(self.custom_configuration.models) > 0
        )

    def get_custom_credentials(self, obfuscated: bool = False) -> Optional[dict]:
        """
        Get custom credentials.

        :param obfuscated: obfuscated secret data in credentials
        :return:
        """
        if self.custom_configuration.provider is None:
            return None

        credentials = self.custom_configuration.provider.credentials
        if not obfuscated:
            return credentials

        # Obfuscate provider credentials
        copy_credentials = credentials.copy()
        return copy_credentials

    def get_custom_model_credentials(
        self, model_type: ModelType, model: str, obfuscated: bool = False
    ) -> Optional[dict]:
        """
        Get custom model credentials.

        :param model_type: model type
        :param model: model name
        :param obfuscated: obfuscated secret data in credentials
        :return:
        """
        if not self.custom_configuration.models:
            return None

        for model_configuration in self.custom_configuration.models:
            if (
                model_configuration.model_type == model_type
                and model_configuration.model == model
            ):
                credentials = model_configuration.credentials
                if not obfuscated:
                    return credentials
                copy_credentials = credentials.copy()
                # Obfuscate credentials
                return copy_credentials

        return None

    def get_provider_instance(self) -> ModelProvider:
        """
        Get provider instance.
        :return:
        """
        return model_provider_factory.get_provider_instance(self.provider.provider)

    def get_model_type_instance(self, model_type: ModelType) -> AIModel:
        """
        Get current model type instance.

        :param model_type: model type
        :return:
        """
        # Get provider instance
        provider_instance = self.get_provider_instance()

        # Get model instance of LLM
        return provider_instance.get_model_instance(model_type)

    def get_provider_model(
        self, model_type: ModelType, model: str, only_active: bool = False
    ) -> Optional[ModelWithProviderEntity]:
        """
        Get provider model.
        :param model_type: model type
        :param model: model name
        :param only_active: return active model only
        :return:
        """
        provider_models = self.get_provider_models(model_type, only_active)

        for provider_model in provider_models:
            if provider_model.model == model:
                return provider_model

        return None

    def get_provider_models(
        self, model_type: Optional[ModelType] = None, only_active: bool = False
    ) -> List[ModelWithProviderEntity]:
        """
        Get provider models.
        :param model_type: model type
        :param only_active: only active models
        :return:
        """
        provider_instance = self.get_provider_instance()

        model_types = []
        if model_type:
            model_types.append(model_type)
        else:
            model_types = provider_instance.get_provider_schema().supported_model_types

        provider_models = self._get_custom_provider_models(
            model_types=model_types, provider_instance=provider_instance
        )
        if only_active:
            provider_models = [
                m for m in provider_models if m.status == ModelStatus.ACTIVE
            ]

        # resort provider_models
        return sorted(provider_models, key=lambda x: x.model_type.value)

    def _get_custom_provider_models(
        self, model_types: List[ModelType], provider_instance: ModelProvider
    ) -> List[ModelWithProviderEntity]:
        """
        Get custom provider models.

        :param model_types: model types
        :param provider_instance: provider instance
        :return:
        """
        provider_models = []

        credentials = None
        if self.custom_configuration.provider:
            credentials = self.custom_configuration.provider.credentials

        for model_type in model_types:
            if model_type not in self.provider.supported_model_types:
                continue

            models = provider_instance.models(model_type)
            for m in models:
                provider_models.append(
                    ModelWithProviderEntity(
                        model=m.model,
                        label=m.label,
                        model_type=m.model_type,
                        features=m.features,
                        fetch_from=m.fetch_from,
                        model_properties=m.model_properties,
                        deprecated=m.deprecated,
                        provider=SimpleModelProviderEntity(self.provider),
                        status=ModelStatus.ACTIVE
                        if credentials
                        else ModelStatus.NO_CONFIGURE,
                    )
                )

        # custom models
        for model_configuration in self.custom_configuration.models:
            if model_configuration.model_type not in model_types:
                continue

            try:
                custom_model_schema = provider_instance.get_model_instance(
                    model_configuration.model_type
                ).get_customizable_model_schema_from_credentials(
                    model_configuration.model, model_configuration.credentials
                )
            except Exception as ex:
                logger.warning(f"get custom model schema failed, {ex}")
                continue

            if not custom_model_schema:
                continue

            provider_models.append(
                ModelWithProviderEntity(
                    model=custom_model_schema.model,
                    label=custom_model_schema.label,
                    model_type=custom_model_schema.model_type,
                    features=custom_model_schema.features,
                    fetch_from=custom_model_schema.fetch_from,
                    model_properties=custom_model_schema.model_properties,
                    deprecated=custom_model_schema.deprecated,
                    provider=SimpleModelProviderEntity(self.provider),
                    status=ModelStatus.ACTIVE,
                )
            )

        return provider_models


class ProviderConfigurations(BaseModel):
    """
    Model class for provider configuration dict.
    """

    configurations: Dict[str, ProviderConfiguration] = {}

    def __init__(self):
        super().__init__()

    def get_models(
        self,
        provider: Optional[str] = None,
        model_type: Optional[ModelType] = None,
        only_active: bool = False,
    ) -> List[ModelWithProviderEntity]:
        """
        Get available models.

        If preferred provider type is `system`:
          Get the current **system mode** if provider supported,
          if all system modes are not available (no quota), it is considered to be the **custom credential mode**.
          If there is no model configured in custom mode, it is treated as no_configure.
        system > custom > no_configure

        If preferred provider type is `custom`:
          If custom credentials are configured, it is treated as custom mode.
          Otherwise, get the current **system mode** if supported,
          If all system modes are not available (no quota), it is treated as no_configure.
        custom > system > no_configure

        If real mode is `system`, use system credentials to get models,
          paid quotas > provider free quotas > system free quotas
          include pre-defined models (exclude GPT-4, status marked as `no_permission`).
        If real mode is `custom`, use workspace custom credentials to get models,
          include pre-defined models, custom models(manual append).
        If real mode is `no_configure`, only return pre-defined models from `model runtime`.
          (model status marked as `no_configure` if preferred provider type is `custom` otherwise `quota_exceeded`)
        model status marked as `active` is available.

        :param provider: provider name
        :param model_type: model type
        :param only_active: only active models
        :return:
        """
        all_models = []
        for provider_configuration in self.values():
            if provider and provider_configuration.provider.provider != provider:
                continue

            all_models.extend(
                provider_configuration.get_provider_models(model_type, only_active)
            )

        return all_models

    def to_list(self) -> List[ProviderConfiguration]:
        """
        Convert to list.

        :return:
        """
        return list(self.values())

    def __getitem__(self, key):
        return self.configurations[key]

    def __setitem__(self, key, value):
        self.configurations[key] = value

    def __iter__(self):
        return iter(self.configurations)

    def values(self) -> Iterator[ProviderConfiguration]:
        return self.configurations.values()

    def get(self, key, default=None):
        return self.configurations.get(key, default)


class ProviderModelBundle(BaseModel):
    """
    Provider model bundle.
    """

    configuration: ProviderConfiguration
    provider_instance: ModelProvider
    model_type_instance: AIModel

    if PYDANTIC_V2:
        model_config = ConfigDict(protected_namespaces=(), arbitrary_types_allowed=True)
    else:

        class Config:
            protected_namespaces = ()

            arbitrary_types_allowed = True

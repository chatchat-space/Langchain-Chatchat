from typing import List, Optional

from model_providers.bootstrap_web.entities.model_provider_entities import (
    CustomConfigurationResponse,
    CustomConfigurationStatus,
    ModelResponse,
    ProviderResponse,
    ProviderWithModelsResponse,
    SystemConfigurationResponse,
)
from model_providers.core.entities.model_entities import ModelStatus
from model_providers.core.entities.provider_entities import ProviderType
from model_providers.core.model_runtime.entities.model_entities import ModelType
from model_providers.core.provider_manager import ProviderManager


class ProvidersWrapper:
    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager

    def get_provider_list(
        self, model_type: Optional[str] = None
    ) -> List[ProviderResponse]:
        """
        get provider list.

        :param model_type: model type
        :return:
        """
        # 合并两个字典的键
        provider = set(
            self.provider_manager.provider_name_to_provider_records_dict.keys()
        )
        provider.update(
            self.provider_manager.provider_name_to_provider_model_records_dict.keys()
        )
        # Get all provider configurations of the current workspace
        provider_configurations = self.provider_manager.get_configurations(
            provider=provider
        )

        provider_responses = []
        for provider_configuration in provider_configurations.values():
            if model_type:
                model_type_entity = ModelType.value_of(model_type)
                if (
                    model_type_entity
                    not in provider_configuration.provider.supported_model_types
                ):
                    continue

            provider_response = ProviderResponse(
                provider=provider_configuration.provider.provider,
                label=provider_configuration.provider.label,
                description=provider_configuration.provider.description,
                icon_small=provider_configuration.provider.icon_small,
                icon_large=provider_configuration.provider.icon_large,
                background=provider_configuration.provider.background,
                help=provider_configuration.provider.help,
                supported_model_types=provider_configuration.provider.supported_model_types,
                configurate_methods=provider_configuration.provider.configurate_methods,
                provider_credential_schema=provider_configuration.provider.provider_credential_schema,
                model_credential_schema=provider_configuration.provider.model_credential_schema,
                preferred_provider_type=ProviderType.value_of("custom"),
                custom_configuration=CustomConfigurationResponse(
                    status=CustomConfigurationStatus.ACTIVE
                    if provider_configuration.is_custom_configuration_available()
                    else CustomConfigurationStatus.NO_CONFIGURE
                ),
                system_configuration=SystemConfigurationResponse(enabled=False),
            )

            provider_responses.append(provider_response)

        return provider_responses

    def get_models_by_model_type(
        self, model_type: str
    ) -> List[ProviderWithModelsResponse]:
        """
        get models by model type.

        :param model_type: model type
        :return:
        """
        # 合并两个字典的键
        provider = set(
            self.provider_manager.provider_name_to_provider_records_dict.keys()
        )
        provider.update(
            self.provider_manager.provider_name_to_provider_model_records_dict.keys()
        )
        # Get all provider configurations of the current workspace
        provider_configurations = self.provider_manager.get_configurations(
            provider=provider
        )

        # Get provider available models
        models = provider_configurations.get_models(
            model_type=ModelType.value_of(model_type)
        )

        # Group models by provider
        provider_models = {}
        for model in models:
            if model.provider.provider not in provider_models:
                provider_models[model.provider.provider] = []

            if model.deprecated:
                continue

            provider_models[model.provider.provider].append(model)

        # convert to ProviderWithModelsResponse list
        providers_with_models: List[ProviderWithModelsResponse] = []
        for provider, models in provider_models.items():
            if not models:
                continue

            first_model = models[0]

            has_active_models = any(
                [model.status == ModelStatus.ACTIVE for model in models]
            )

            providers_with_models.append(
                ProviderWithModelsResponse(
                    provider=provider,
                    label=first_model.provider.label,
                    icon_small=first_model.provider.icon_small,
                    icon_large=first_model.provider.icon_large,
                    status=CustomConfigurationStatus.ACTIVE
                    if has_active_models
                    else CustomConfigurationStatus.NO_CONFIGURE,
                    models=[
                        ModelResponse(
                            model=model.model,
                            label=model.label,
                            model_type=model.model_type,
                            features=model.features,
                            fetch_from=model.fetch_from,
                            model_properties=model.model_properties,
                            status=model.status,
                        )
                        for model in models
                    ],
                )
            )

        return providers_with_models

import json
from collections import defaultdict
from json import JSONDecodeError
from typing import List, Optional, Union

from model_providers.core.entities.model_entities import (
    DefaultModelEntity,
    DefaultModelProviderEntity,
)
from model_providers.core.entities.provider_configuration import (
    ProviderConfiguration,
    ProviderConfigurations,
    ProviderModelBundle,
)
from model_providers.core.entities.provider_entities import (
    CustomConfiguration,
    CustomModelConfiguration,
    CustomProviderConfiguration,
)
from model_providers.core.model_runtime.entities.model_entities import ModelType
from model_providers.core.model_runtime.entities.provider_entities import (
    CredentialFormSchema,
    FormType,
    ProviderEntity,
)
from model_providers.core.model_runtime.model_providers import model_provider_factory


class ProviderManager:
    """
    ProviderManager is a class that manages the model providers includes Hosting and Customize Model Providers.
    """

    def __init__(
        self,
        provider_name_to_provider_records_dict: dict,
        provider_name_to_provider_model_records_dict: dict,
    ) -> None:
        self.provider_name_to_provider_records_dict = (
            provider_name_to_provider_records_dict
        )
        self.provider_name_to_provider_model_records_dict = (
            provider_name_to_provider_model_records_dict
        )

    def get_configurations(self, provider: Union[str, set]) -> ProviderConfigurations:
        """
        Get model provider configurations.

        Construct ProviderConfiguration objects for each provider
        Including:
        1. Basic information of the provider
        2. Hosting configuration information, including:
          (1. Whether to enable (support) hosting type, if enabled, the following information exists
          (2. List of hosting type provider configurations
              (including quota type, quota limit, current remaining quota, etc.)
          (3. The current hosting type in use (whether there is a quota or not)
              paid quotas > provider free quotas > hosting trial quotas
          (4. Unified credentials for hosting providers
        3. Custom configuration information, including:
          (1. Whether to enable (support) custom type, if enabled, the following information exists
          (2. Custom provider configuration (including credentials)
          (3. List of custom provider model configurations (including credentials)
        4. Hosting/custom preferred provider type.
        Provide methods:
        - Get the current configuration (including credentials)
        - Get the availability and status of the hosting configuration: active available,
          quota_exceeded insufficient quota, unsupported hosting
        - Get the availability of custom configuration
          Custom provider available conditions:
          (1. custom provider credentials available
          (2. at least one custom model credentials available
        - Verify, update, and delete custom provider configuration
        - Verify, update, and delete custom provider model configuration
        - Get the list of available models (optional provider filtering, model type filtering)
          Append custom provider models to the list
        - Get provider instance
        - Switch selection priority

        :param: provider
        :return:
        """

        # Get all provider entities
        provider_entities = model_provider_factory.get_providers(provider_name=provider)

        provider_configurations = ProviderConfigurations()

        # Construct ProviderConfiguration objects for each provider
        for provider_entity in provider_entities:
            provider_name = provider_entity.provider

            provider_credentials = self.provider_name_to_provider_records_dict.get(
                provider_entity.provider
            )
            if not provider_credentials:
                provider_credentials = {}

            provider_model_records = (
                self.provider_name_to_provider_model_records_dict.get(
                    provider_entity.provider
                )
            )
            if not provider_model_records:
                provider_model_records = []

            # Convert to custom configuration
            custom_configuration = self._to_custom_configuration(
                provider_entity, provider_credentials, provider_model_records
            )

            provider_configuration = ProviderConfiguration(
                provider=provider_entity, custom_configuration=custom_configuration
            )

            provider_configurations[provider_name] = provider_configuration

        # Return the encapsulated object
        return provider_configurations

    def get_provider_model_bundle(
        self, provider: str, model_type: ModelType
    ) -> ProviderModelBundle:
        """
        Get provider model bundle.
        :param provider: provider name
        :param model_type: model type
        :return:
        """
        provider_configurations = self.get_configurations(provider=provider)

        # get provider instance
        provider_configuration = provider_configurations.get(provider)
        if not provider_configuration:
            raise ValueError(f"Provider {provider} does not exist.")

        provider_instance = provider_configuration.get_provider_instance()
        model_type_instance = provider_instance.get_model_instance(model_type)

        return ProviderModelBundle(
            configuration=provider_configuration,
            provider_instance=provider_instance,
            model_type_instance=model_type_instance,
        )

    def get_default_model(self, model_type: ModelType) -> Optional[DefaultModelEntity]:
        """
        Get default model.

        :param model_type: model type
        :return:
        """

        default_model = {}
        # Get provider configurations
        provider_configurations = self.get_configurations(provider="openai")

        # get available models from provider_configurations
        available_models = provider_configurations.get_models(
            model_type=model_type, only_active=True
        )

        if available_models:
            found = False
            for available_model in available_models:
                if available_model.model == "gpt-3.5-turbo-1106":
                    default_model = {
                        "provider_name": available_model.provider.provider,
                        "model_name": available_model.model,
                    }
                    found = True
                    break

            if not found:
                available_model = available_models[0]
                default_model = {
                    "provider_name": available_model.provider.provider,
                    "model_name": available_model.model,
                }

        provider_instance = model_provider_factory.get_provider_instance(
            default_model.get("provider_name")
        )
        provider_schema = provider_instance.get_provider_schema()

        return DefaultModelEntity(
            model=default_model.get("model_name"),
            model_type=model_type,
            provider=DefaultModelProviderEntity(
                provider=provider_schema.provider,
                label=provider_schema.label,
                icon_small=provider_schema.icon_small,
                icon_large=provider_schema.icon_large,
                supported_model_types=provider_schema.supported_model_types,
            ),
        )

    def _to_custom_configuration(
        self,
        provider_entity: ProviderEntity,
        provider_credentials: dict,
        provider_model_records: List[dict],
    ) -> CustomConfiguration:
        """
        Convert to custom configuration.

        :param provider_entity: provider entity
        :param provider_credentials: provider records_credentials
        :param provider_model_records: provider model records_credentials
        :return:
        """
        # Get provider credential secret variables
        provider_credential_secret_variables = self._extract_variables(
            provider_entity.provider_credential_schema.credential_form_schemas
            if provider_entity.provider_credential_schema
            else []
        )

        for variable in provider_credential_secret_variables:
            if variable in provider_credentials:
                try:
                    provider_credentials[variable] = provider_credentials.get(variable)
                except ValueError:
                    pass
        custom_provider_configuration = CustomProviderConfiguration(
            credentials=provider_credentials
        )

        # Get provider model credential secret variables
        model_credential_variables = self._extract_variables(
            provider_entity.model_credential_schema.credential_form_schemas
            if provider_entity.model_credential_schema
            else []
        )

        # Get custom provider model credentials
        custom_model_configurations = []
        for provider_model_record in provider_model_records:
            if not provider_model_record.get("model_credentials"):
                continue

            provider_model_credentials = {}
            for variable in model_credential_variables:
                if variable in provider_model_record.get("model_credentials"):
                    try:
                        provider_model_credentials[
                            variable
                        ] = provider_model_record.get("model_credentials").get(variable)
                    except ValueError:
                        pass

            custom_model_configurations.append(
                CustomModelConfiguration(
                    model=provider_model_record.get("model"),
                    model_type=ModelType.value_of(
                        provider_model_record.get("model_type")
                    ),
                    credentials=provider_model_credentials,
                )
            )

        return CustomConfiguration(
            provider=custom_provider_configuration, models=custom_model_configurations
        )

    def _extract_variables(
        self, credential_form_schemas: List[CredentialFormSchema]
    ) -> List[str]:
        """
        Extract input form variables.

        :param credential_form_schemas:
        :return:
        """
        input_form_variables = []
        for credential_form_schema in credential_form_schemas:
            input_form_variables.append(credential_form_schema.variable)

        return input_form_variables

from enum import Enum
from typing import List, Literal, Optional

from model_providers.core.entities.model_entities import (
    ModelStatus,
    ModelWithProviderEntity,
)
from model_providers.core.entities.provider_entities import (
    ProviderQuotaType,
    ProviderType,
    QuotaConfiguration,
)
from model_providers.core.model_runtime.entities.common_entities import I18nObject
from model_providers.core.model_runtime.entities.model_entities import (
    ModelType,
    ProviderModel,
)
from model_providers.core.model_runtime.entities.provider_entities import (
    ConfigurateMethod,
    ModelCredentialSchema,
    ProviderCredentialSchema,
    ProviderHelpEntity,
    SimpleProviderEntity,
)

from ..._compat import PYDANTIC_V2, ConfigDict
from ..._models import BaseModel


class CustomConfigurationStatus(Enum):
    """
    Enum class for custom configuration status.
    """

    ACTIVE = "active"
    NO_CONFIGURE = "no-configure"


class CustomConfigurationResponse(BaseModel):
    """
    Model class for provider custom configuration response.
    """

    status: CustomConfigurationStatus


class SystemConfigurationResponse(BaseModel):
    """
    Model class for provider system configuration response.
    """

    enabled: bool
    current_quota_type: Optional[ProviderQuotaType] = None
    quota_configurations: List[QuotaConfiguration] = []


class ProviderResponse(BaseModel):
    """
    Model class for provider response.
    """

    provider: str
    label: I18nObject
    description: Optional[I18nObject] = None
    icon_small: Optional[I18nObject] = None
    icon_large: Optional[I18nObject] = None
    background: Optional[str] = None
    help: Optional[ProviderHelpEntity] = None
    supported_model_types: List[ModelType]
    configurate_methods: List[ConfigurateMethod]
    provider_credential_schema: Optional[ProviderCredentialSchema] = None
    model_credential_schema: Optional[ModelCredentialSchema] = None
    preferred_provider_type: ProviderType
    custom_configuration: CustomConfigurationResponse
    system_configuration: SystemConfigurationResponse
    if PYDANTIC_V2:
        model_config = ConfigDict(protected_namespaces=())
    else:

        class Config:
            protected_namespaces = ()

    def __init__(self, **data) -> None:
        super().__init__(**data)
        #
        # url_prefix = (current_app.config.get("CONSOLE_API_URL")
        #               + f"/console/api/workspaces/current/model-providers/{self.provider}")
        # if self.icon_small is not None:
        #     self.icon_small = I18nObject(
        #         en_US=f"{url_prefix}/icon_small/en_US",
        #         zh_Hans=f"{url_prefix}/icon_small/zh_Hans"
        #     )
        #
        # if self.icon_large is not None:
        #     self.icon_large = I18nObject(
        #         en_US=f"{url_prefix}/icon_large/en_US",
        #         zh_Hans=f"{url_prefix}/icon_large/zh_Hans"
        #     )


class ProviderListResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[ProviderResponse] = []


class ModelResponse(ProviderModel):
    """
    Model class for model response.
    """

    status: ModelStatus


class ProviderWithModelsResponse(BaseModel):
    """
    Model class for provider with models response.
    """

    provider: str
    label: I18nObject
    icon_small: Optional[I18nObject] = None
    icon_large: Optional[I18nObject] = None
    status: CustomConfigurationStatus
    models: List[ModelResponse]

    def __init__(self, **data) -> None:
        super().__init__(**data)

        # url_prefix = (current_app.config.get("CONSOLE_API_URL")
        #               + f"/console/api/workspaces/current/model-providers/{self.provider}")
        # if self.icon_small is not None:
        #     self.icon_small = I18nObject(
        #         en_US=f"{url_prefix}/icon_small/en_US",
        #         zh_Hans=f"{url_prefix}/icon_small/zh_Hans"
        #     )
        #
        # if self.icon_large is not None:
        #     self.icon_large = I18nObject(
        #         en_US=f"{url_prefix}/icon_large/en_US",
        #         zh_Hans=f"{url_prefix}/icon_large/zh_Hans"
        #     )


class ProviderModelTypeResponse(BaseModel):
    object: Literal["list"] = "list"
    data: List[ProviderWithModelsResponse] = []


class SimpleProviderEntityResponse(SimpleProviderEntity):
    """
    Simple provider entity response.
    """

    def __init__(self, **data) -> None:
        super().__init__(**data)

        # url_prefix = (current_app.config.get("CONSOLE_API_URL")
        #               + f"/console/api/workspaces/current/model-providers/{self.provider}")
        # if self.icon_small is not None:
        #     self.icon_small = I18nObject(
        #         en_US=f"{url_prefix}/icon_small/en_US",
        #         zh_Hans=f"{url_prefix}/icon_small/zh_Hans"
        #     )
        #
        # if self.icon_large is not None:
        #     self.icon_large = I18nObject(
        #         en_US=f"{url_prefix}/icon_large/en_US",
        #         zh_Hans=f"{url_prefix}/icon_large/zh_Hans"
        #     )


class DefaultModelResponse(BaseModel):
    """
    Default model entity.
    """

    model: str
    model_type: ModelType
    provider: SimpleProviderEntityResponse

    if PYDANTIC_V2:
        model_config = ConfigDict(protected_namespaces=())
    else:

        class Config:
            protected_namespaces = ()


class ModelWithProviderEntityResponse(ModelWithProviderEntity):
    """
    Model with provider entity.
    """

    provider: SimpleProviderEntityResponse

    def __init__(self, model: ModelWithProviderEntity) -> None:
        super().__init__(**model.dict())

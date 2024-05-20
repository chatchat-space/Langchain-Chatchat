from enum import Enum
from typing import List, Optional

from model_providers.core.model_runtime.entities.model_entities import ModelType

from ..._compat import PYDANTIC_V2, ConfigDict
from ..._models import BaseModel


class ProviderType(Enum):
    CUSTOM = "custom"
    SYSTEM = "system"

    @staticmethod
    def value_of(value):
        for member in ProviderType:
            if member.value == value:
                return member
        raise ValueError(f"No matching enum found for value '{value}'")


class ProviderQuotaType(Enum):
    PAID = "paid"
    """hosted paid quota"""

    FREE = "free"
    """third-party free quota"""

    TRIAL = "trial"
    """hosted trial quota"""

    @staticmethod
    def value_of(value):
        for member in ProviderQuotaType:
            if member.value == value:
                return member
        raise ValueError(f"No matching enum found for value '{value}'")


class QuotaUnit(Enum):
    TIMES = "times"
    TOKENS = "tokens"
    CREDITS = "credits"


class SystemConfigurationStatus(Enum):
    """
    Enum class for system configuration status.
    """

    ACTIVE = "active"
    QUOTA_EXCEEDED = "quota-exceeded"
    UNSUPPORTED = "unsupported"


class RestrictModel(BaseModel):
    model: str
    base_model_name: Optional[str] = None
    model_type: ModelType

    if PYDANTIC_V2:
        model_config = ConfigDict(protected_namespaces=())
    else:

        class Config:
            protected_namespaces = ()


class QuotaConfiguration(BaseModel):
    """
    Model class for provider quota configuration.
    """

    quota_type: ProviderQuotaType
    quota_unit: QuotaUnit
    quota_limit: int
    quota_used: int
    is_valid: bool
    restrict_models: List[RestrictModel] = []


class SystemConfiguration(BaseModel):
    """
    Model class for provider system configuration.
    """

    enabled: bool
    current_quota_type: Optional[ProviderQuotaType] = None
    quota_configurations: List[QuotaConfiguration] = []
    credentials: Optional[dict] = None


class CustomProviderConfiguration(BaseModel):
    """
    Model class for provider custom configuration.
    """

    credentials: dict


class CustomModelConfiguration(BaseModel):
    """
    Model class for provider custom model configuration.
    """

    model: str
    model_type: ModelType
    credentials: dict

    if PYDANTIC_V2:
        model_config = ConfigDict(protected_namespaces=())
    else:

        class Config:
            protected_namespaces = ()


class CustomConfiguration(BaseModel):
    """
    Model class for provider custom configuration.
    """

    provider: Optional[CustomProviderConfiguration] = None
    models: List[CustomModelConfiguration] = []

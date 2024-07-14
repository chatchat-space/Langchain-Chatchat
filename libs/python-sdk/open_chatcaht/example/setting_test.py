from __future__ import annotations

from pydantic_settings import YamlConfigSettingsSource, BaseSettings
from pydantic_settings.sources import PathType, DEFAULT_PATH

from libs.sdk.default_config import default_config
from libs.sdk.v1.chatchat_api_config import ChatchatApiConfig
default_config.default_chunk_size = 2222
c = ChatchatApiConfig()
print(c.chunk_size)

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.append(str(Path(__file__).parent))
import _core_config as core_config

logger = logging.getLogger()


class ConfigServer(core_config.Config):
    HTTPX_DEFAULT_TIMEOUT: Optional[float] = None
    """httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。"""
    OPEN_CROSS_DOMAIN: Optional[bool] = None
    """API 是否开启跨域，默认为False，如果需要开启，请设置为True"""
    DEFAULT_BIND_HOST: Optional[str] = None
    """各服务器默认绑定host。如改为"0.0.0.0"需要修改下方所有XX_SERVER的host"""
    WEBUI_SERVER_PORT: Optional[int] = None
    """webui port"""
    API_SERVER_PORT: Optional[int] = None
    """api port"""
    WEBUI_SERVER: Optional[Dict[str, Any]] = None
    """webui.py server"""
    API_SERVER: Optional[Dict[str, Any]] = None
    """api.py server"""

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return self.to_json()


@dataclass
class ConfigServerFactory(core_config.ConfigFactory[ConfigServer]):
    """Server 配置工厂类"""

    def __init__(self):
        # httpx 请求默认超时时间（秒）。如果加载模型或对话较慢，出现超时错误，可以适当加大该值。
        self.HTTPX_DEFAULT_TIMEOUT = 300.0

        # API 是否开启跨域，默认为False，如果需要开启，请设置为True
        # is open cross domain
        self.OPEN_CROSS_DOMAIN = True

        # 各服务器默认绑定host。如改为"0.0.0.0"需要修改下方所有XX_SERVER的host
        self.DEFAULT_BIND_HOST = "127.0.0.1" if sys.platform != "win32" else "127.0.0.1"
        self.WEBUI_SERVER_PORT = 8501
        self.API_SERVER_PORT = 7861
        self.__init_server()

    def __init_server(self):
        # webui.py server
        self.WEBUI_SERVER = {
            "host": self.DEFAULT_BIND_HOST,
            "port": self.WEBUI_SERVER_PORT,
        }

        # api.py server
        self.API_SERVER = {
            "host": self.DEFAULT_BIND_HOST,
            "port": self.API_SERVER_PORT,
        }

    def httpx_default_timeout(self, timeout: float):
        self.HTTPX_DEFAULT_TIMEOUT = timeout

    def open_cross_domain(self, open_cross_domain: bool):
        self.OPEN_CROSS_DOMAIN = open_cross_domain

    def default_bind_host(self, default_bind_host: str):
        self.DEFAULT_BIND_HOST = default_bind_host
        self.__init_server()

    def webui_server_port(self, webui_server_port: int):
        self.WEBUI_SERVER_PORT = webui_server_port
        self.__init_server()

    def api_server_port(self, api_server_port: int):
        self.API_SERVER_PORT = api_server_port
        self.__init_server()

    def get_config(self) -> ConfigServer:
        config = ConfigServer()
        config.HTTPX_DEFAULT_TIMEOUT = self.HTTPX_DEFAULT_TIMEOUT
        config.OPEN_CROSS_DOMAIN = self.OPEN_CROSS_DOMAIN
        config.DEFAULT_BIND_HOST = self.DEFAULT_BIND_HOST
        config.WEBUI_SERVER_PORT = self.WEBUI_SERVER_PORT
        config.API_SERVER_PORT = self.API_SERVER_PORT
        config.WEBUI_SERVER = self.WEBUI_SERVER
        config.API_SERVER = self.API_SERVER
        return config


class ConfigServerWorkSpace(
    core_config.ConfigWorkSpace[ConfigServerFactory, ConfigServer]
):
    """
    工作空间的配置预设，提供ConfigServer建造方法产生实例。
    """

    config_factory_cls = ConfigServerFactory

    def __init__(self):
        super().__init__()

    def _build_config_factory(self, config_json: Any) -> ConfigServerFactory:
        _config_factory = self.config_factory_cls()
        if config_json.get("HTTPX_DEFAULT_TIMEOUT") is not None:
            _config_factory.httpx_default_timeout(config_json["HTTPX_DEFAULT_TIMEOUT"])
        if config_json.get("OPEN_CROSS_DOMAIN") is not None:
            _config_factory.open_cross_domain(config_json["OPEN_CROSS_DOMAIN"])
        if config_json.get("DEFAULT_BIND_HOST") is not None:
            _config_factory.default_bind_host(config_json["DEFAULT_BIND_HOST"])
        if config_json.get("WEBUI_SERVER_PORT") is not None:
            _config_factory.webui_server_port(config_json["WEBUI_SERVER_PORT"])
        if config_json.get("API_SERVER_PORT") is not None:
            _config_factory.api_server_port(config_json["API_SERVER_PORT"])

        return _config_factory

    @classmethod
    def get_type(cls) -> str:
        return ConfigServer.class_name()

    def get_config(self) -> ConfigServer:
        return self._config_factory.get_config()

    def set_httpx_default_timeout(self, timeout: float):
        self._config_factory.httpx_default_timeout(timeout)
        self.store_config()

    def set_open_cross_domain(self, open_cross_domain: bool):
        self._config_factory.open_cross_domain(open_cross_domain)
        self.store_config()

    def set_default_bind_host(self, default_bind_host: str):
        self._config_factory.default_bind_host(default_bind_host)
        self.store_config()

    def set_webui_server_port(self, webui_server_port: int):
        self._config_factory.webui_server_port(webui_server_port)
        self.store_config()

    def set_api_server_port(self, api_server_port: int):
        self._config_factory.api_server_port(api_server_port)
        self.store_config()


config_server_workspace: ConfigServerWorkSpace = ConfigServerWorkSpace()

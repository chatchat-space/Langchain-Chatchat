from omegaconf import DictConfig, OmegaConf

from model_providers.bootstrap_web.openai_bootstrap_web import (
    RESTFulOpenAIBootstrapBaseWeb,
)
from model_providers.core.bootstrap import OpenAIBootstrapBaseWeb
from model_providers.core.model_manager import ModelManager


def _to_custom_provide_configuration(cfg: DictConfig):
    """
    ```
        openai:
          model_credential:
            - model: 'gpt-3.5-turbo'
              model_credentials:
                openai_api_key: ''
                openai_organization: ''
                openai_api_base: ''
            - model: 'gpt-4'
              model_credentials:
                openai_api_key: ''
                openai_organization: ''
                openai_api_base: ''

          provider_credential:
            openai_api_key: ''
            openai_organization: ''
            openai_api_base: ''

    ```
    :param model_providers_cfg:
    :return:
    """
    provider_name_to_provider_records_dict = {}
    provider_name_to_provider_model_records_dict = {}

    for key, item in cfg.items():
        model_credential = item.get("model_credential")
        provider_credential = item.get("provider_credential")
        # 转换omegaconf对象为基本属性
        if model_credential:
            model_credential = OmegaConf.to_container(model_credential)
            provider_name_to_provider_model_records_dict[key] = model_credential
        if provider_credential:
            provider_credential = OmegaConf.to_container(provider_credential)
            provider_name_to_provider_records_dict[key] = provider_credential

    return (
        provider_name_to_provider_records_dict,
        provider_name_to_provider_model_records_dict,
    )


class BootstrapWebBuilder:
    """
    创建一个模型实例创建工具
    """

    _model_providers_cfg_path: str
    _host: str
    _port: int

    def model_providers_cfg_path(self, model_providers_cfg_path: str):
        self._model_providers_cfg_path = model_providers_cfg_path
        return self

    def host(self, host: str):
        self._host = host
        return self

    def port(self, port: int):
        self._port = port
        return self

    def build(self) -> OpenAIBootstrapBaseWeb:
        assert (
            self._model_providers_cfg_path is not None
            and self._host is not None
            and self._port is not None
        )
        # 读取配置文件
        cfg = OmegaConf.load(self._model_providers_cfg_path)
        # 转换配置文件
        (
            provider_name_to_provider_records_dict,
            provider_name_to_provider_model_records_dict,
        ) = _to_custom_provide_configuration(cfg)
        # 创建模型管理器
        provider_manager = ModelManager(
            provider_name_to_provider_records_dict,
            provider_name_to_provider_model_records_dict,
        )
        # 创建web服务
        restful = RESTFulOpenAIBootstrapBaseWeb.from_config(
            cfg={"host": self._host, "port": self._port}
        )
        restful.provider_manager = provider_manager
        return restful

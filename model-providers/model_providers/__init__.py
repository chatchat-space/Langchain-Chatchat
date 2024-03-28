from model_providers.core.model_manager import ModelManager

from omegaconf import OmegaConf, DictConfig


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
        model_credential = item.get('model_credential')
        provider_credential = item.get('provider_credential')
        # 转换omegaconf对象为基本属性
        if model_credential:
            model_credential = OmegaConf.to_container(model_credential)
            provider_name_to_provider_model_records_dict[key] = model_credential
        if provider_credential:
            provider_credential = OmegaConf.to_container(provider_credential)
            provider_name_to_provider_records_dict[key] = provider_credential

    return provider_name_to_provider_records_dict, provider_name_to_provider_model_records_dict


model_providers_cfg = OmegaConf.load("/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/model-providers/model_providers.yaml")
provider_name_to_provider_records_dict, provider_name_to_provider_model_records_dict = _to_custom_provide_configuration(
    cfg=model_providers_cfg)
# 基于配置管理器创建的模型实例
provider_manager = ModelManager(
    provider_name_to_provider_records_dict=provider_name_to_provider_records_dict,
    provider_name_to_provider_model_records_dict=provider_name_to_provider_model_records_dict
)

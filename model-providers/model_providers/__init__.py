from chatchat.configs import MODEL_PLATFORMS
from model_providers.core.model_manager import ModelManager

def _to_custom_provide_configuration():
    provider_name_to_provider_records_dict = {}
    provider_name_to_provider_model_records_dict = {}
    return provider_name_to_provider_records_dict, provider_name_to_provider_model_records_dict

# 基于配置管理器创建的模型实例
provider_manager = ModelManager(
    provider_name_to_provider_records_dict={
        'openai': {
            'openai_api_key': "sk-4M9LYF",
        }
    },
    provider_name_to_provider_model_records_dict={}
)
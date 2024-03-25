import os
from typing import cast, Generator

from chatchat_model_providers.core.model_runtime.entities.llm_entities import LLMResultChunk, LLMResultChunkDelta
from chatchat_model_providers.core.model_runtime.entities.message_entities import UserPromptMessage, AssistantPromptMessage
from chatchat_model_providers.core.model_runtime.entities.model_entities import ModelType

if __name__ == '__main__':
    # 基于配置管理器创建的模型实例
    # provider_manager = ProviderManager()

    provider_configurations = ProviderConfigurations(
        tenant_id=tenant_id
    )


    #
    # model_instance = ModelInstance(
    #     provider_model_bundle=provider_model_bundle,
    #     model=model_config.model,
    # )
    # 直接通过模型加载器创建的模型实例
    from chatchat_model_providers.core.model_runtime.model_providers import model_provider_factory
    model_provider_factory.get_providers(provider_name='openai')
    provider_instance = model_provider_factory.get_provider_instance('openai')
    model_type_instance = provider_instance.get_model_instance(ModelType.LLM)
    print(model_type_instance)
    response = model_type_instance.invoke(
        model='gpt-4',
        credentials={
            'openai_api_key': "sk-",
            'minimax_api_key': os.environ.get('MINIMAX_API_KEY'),
            'minimax_group_id': os.environ.get('MINIMAX_GROUP_ID')
        },
        prompt_messages=[
            UserPromptMessage(
                content='北京今天的天气怎么样'
            )
        ],
        model_parameters={
            'temperature': 0.7,
            'top_p': 1.0,
            'top_k': 1,
            'plugin_web_search': True,
        },
        stop=['you'],
        stream=True,
        user="abc-123"
    )

    assert isinstance(response, Generator)
    total_message = ''
    for chunk in response:
        assert isinstance(chunk, LLMResultChunk)
        assert isinstance(chunk.delta, LLMResultChunkDelta)
        assert isinstance(chunk.delta.message, AssistantPromptMessage)
        total_message += chunk.delta.message.content
        assert len(chunk.delta.message.content) > 0 if not chunk.delta.finish_reason else True
    print(total_message)
    assert '参考资料' in total_message

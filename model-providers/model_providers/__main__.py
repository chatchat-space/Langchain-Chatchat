import os
from typing import cast, Generator

from model_providers import provider_manager
from model_providers.core.model_manager import ModelManager
from model_providers.core.model_runtime.entities.llm_entities import LLMResultChunk, LLMResultChunkDelta
from model_providers.core.model_runtime.entities.message_entities import UserPromptMessage, AssistantPromptMessage
from model_providers.core.model_runtime.entities.model_entities import ModelType

if __name__ == '__main__':
    # 基于配置管理器创建的模型实例

    # Invoke model
    model_instance = provider_manager.get_model_instance(provider='openai', model_type=ModelType.LLM, model='gpt-4')

    response = model_instance.invoke_llm(

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

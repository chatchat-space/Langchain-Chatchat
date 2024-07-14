import { ModelProviderCard } from '@/types/llm';

const ChatChat: ModelProviderCard = {
  id: 'chatchat',
  chatModels: [
    {
      id: 'chatglm3-6b',
      tokens: 4000,
      displayName: 'chatglm3-6b',
      functionCall: true,
    },
    {
      id: 'chatglm_turbo',
      tokens: 4000,
      displayName: 'chatglm_turbo',
    },
    {
      id: 'chatglm_std',
      tokens: 4000,
      displayName: 'chatglm_std',
    },
    {
      id: 'chatglm_lite',
      tokens: 4000,
      displayName: 'chatglm_lite',
    },
    {
      id: 'qwen-turbo',
      tokens: 4000,
      displayName: 'qwen-turbo',
      functionCall: true,
    },
    {
      id: 'qwen-plus',
      tokens: 4000,
      displayName: 'qwen-plus',
    },
    {
      id: 'qwen-max',
      tokens: 4000,
      displayName: 'qwen-max',
    },
    {
      id: 'qwen:7b',
      tokens: 4000,
      displayName: 'qwen:7b',
      functionCall: true,
    },
    {
      id: 'qwen:14b',
      tokens: 4000,
      displayName: 'qwen:14b',
      functionCall: true,
    },
    {
      id: 'qwen-max-longcontext',
      tokens: 4000,
      displayName: 'qwen-max-longcontext',
    },
    {
      id: 'ERNIE-Bot',
      tokens: 4000,
      displayName: 'ERNIE-Bot',
    },
    {
      id: 'ERNIE-Bot-turbo',
      tokens: 4000,
      displayName: 'ERNIE-Bot-turbo',
    },
    {
      id: 'ERNIE-Bot-4',
      tokens: 4000,
      displayName: 'ERNIE-Bot-4',
    },
    {
      id: 'SparkDesk',
      tokens: 4000,
      displayName: 'SparkDesk',
    }
  ]
}

export default ChatChat;
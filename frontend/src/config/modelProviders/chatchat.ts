import { ModelProviderCard } from '@/types/llm';

const ChatChat: ModelProviderCard = {
  id: 'chatchat',
  chatModels: [
    {
      id: 'chatglm_pro',
      tokens: 128_000,
      displayName: 'chatglm_pro'
    },
    {
      id: 'gpt-4-turbo-2024-04-09',
      tokens: 128_000,
      displayName: 'gpt-4-turbo-2024-04-09',
      vision: true,
    }
  ]
}

export default ChatChat;
import { Input, Flex } from 'antd';
import { useTheme } from 'antd-style';
import { memo } from 'react';
import { useTranslation } from 'react-i18next';
import Avatar from 'next/image';

import { imageUrl } from '@/const/url';

import { ModelProvider } from '@/libs/agent-runtime';

import Checker from '../components/Checker';
import ProviderConfig from '../components/ProviderConfig';
import { LLMProviderBaseUrlKey, LLMProviderConfigKey } from '../const';
import ModelSelector from '../components/ModelSeletor';

const providerKey = 'chatchat';

const ChatChatProvider = memo(() => {
  const { t } = useTranslation('setting');
  const theme = useTheme();

  return (
    <ProviderConfig
      configItems={[
        {
          children: <Input allowClear placeholder={t('llm.ChatChat.endpoint.placeholder')} />,
          desc: t('llm.ChatChat.endpoint.desc'),
          label: t('llm.ChatChat.endpoint.title'),
          name: [LLMProviderConfigKey, providerKey, LLMProviderBaseUrlKey],
        },
        {
          children: (
            <Input.TextArea
              allowClear
              placeholder={t('llm.ChatChat.customModelName.placeholder')}
              style={{ height: 100 }}
            />
          ),
          desc: t('llm.ChatChat.customModelName.desc'),
          label: t('llm.ChatChat.customModelName.title'),
          name: [LLMProviderConfigKey, providerKey, 'customModelName'],
        },
        {
          children: <ModelSelector provider={ModelProvider.ChatChat} />,
          desc: t('llm.selectorModel.desc'),
          label: t('llm.selectorModel.title'),
        },
        {
          children: <Checker model={'gml-4'} provider={ModelProvider.ChatChat} />,
          desc: t('llm.ChatChat.checker.desc'),
          label: t('llm.checker.title'),
          minWidth: undefined,
        },
      ]}
      provider={providerKey}
      title={
        <Flex>
          <Avatar
            alt={'Chatchat'}
            height={24}
            src={imageUrl('logo.png')}
            width={24}
          />
          { 'ChatChat' }
        </Flex>
      }
    />
  );
});

export default ChatChatProvider;

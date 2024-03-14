import {
  Anthropic,
  Azure,
  Bedrock,
  Google,
  Mistral,
  Moonshot,
  Ollama,
  OpenAI,
  Perplexity,
  Zhipu,
} from '@lobehub/icons';
import { memo } from 'react';
import { Center } from 'react-layout-kit';

import { ModelProvider } from '@/libs/agent-runtime';

interface ModelProviderIconProps {
  provider?: string;
}

const ModelProviderIcon = memo<ModelProviderIconProps>(({ provider }) => {
  switch (provider) {
    case ModelProvider.ZhiPu: {
      return <Zhipu size={20} />;
    }

    case ModelProvider.Bedrock: {
      return <Bedrock size={20} />;
    }

    case ModelProvider.Google: {
      return (
        <Center height={20} width={20}>
          <Google size={14} />
        </Center>
      );
    }

    case ModelProvider.Azure: {
      return (
        <Center height={20} width={20}>
          <Azure size={14} />
        </Center>
      );
    }

    case ModelProvider.Moonshot: {
      return <Moonshot size={20} />;
    }

    case ModelProvider.OpenAI: {
      return <OpenAI size={20} />;
    }

    case ModelProvider.Ollama: {
      return <Ollama size={20} />;
    }

    case ModelProvider.Perplexity: {
      return <Perplexity size={20} />;
    }

    case ModelProvider.Mistral: {
      return <Mistral size={20} />;
    }

    case ModelProvider.Anthropic: {
      return <Anthropic size={20} />;
    }

    default: {
      return null;
    }
  }
});

export default ModelProviderIcon;

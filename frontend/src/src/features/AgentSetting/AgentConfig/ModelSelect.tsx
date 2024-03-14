import { Select, SelectProps } from 'antd';
import { createStyles } from 'antd-style';
import isEqual from 'fast-deep-equal';
import { memo, useMemo } from 'react';

import { ModelItemRender, ProviderItemRender } from '@/components/ModelSelect';
import { useGlobalStore } from '@/store/global';
import { modelProviderSelectors } from '@/store/global/selectors';
import { ModelProviderCard } from '@/types/llm';

import { useStore } from '../store';

const useStyles = createStyles(({ css, prefixCls }) => ({
  select: css`
    .${prefixCls}-select-dropdown .${prefixCls}-select-item-option-grouped {
      padding-inline-start: 12px;
    }
  `,
}));
interface ModelOption {
  label: any;
  provider: string;
  value: string;
}

const ModelSelect = memo(() => {
  const [model, updateConfig] = useStore((s) => [s.config.model, s.setAgentConfig]);
  const select = useGlobalStore(modelProviderSelectors.modelSelectList, isEqual);
  const { styles } = useStyles();

  const enabledList = select.filter((s) => s.enabled);

  const options = useMemo<SelectProps['options']>(() => {
    const getChatModels = (provider: ModelProviderCard) =>
      provider.chatModels
        .filter((c) => !c.hidden)
        .map((model) => ({
          label: <ModelItemRender {...model} />,
          provider: provider.id,
          value: model.id,
        }));

    if (enabledList.length === 1) {
      const provider = enabledList[0];

      return getChatModels(provider);
    }

    return enabledList.map((provider) => ({
      label: <ProviderItemRender provider={provider.id} />,
      options: getChatModels(provider),
    }));
  }, [enabledList]);

  return (
    <Select
      className={styles.select}
      onChange={(model, option) => {
        updateConfig({
          model,
          provider: (option as unknown as ModelOption).provider,
        });
      }}
      options={options}
      popupMatchSelectWidth={false}
      value={model}
    />
  );
});

export default ModelSelect;

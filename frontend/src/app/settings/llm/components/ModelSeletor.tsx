import { CheckCircleFilled } from '@ant-design/icons';
import { Alert, Highlighter } from '@lobehub/ui';
import { Button } from 'antd';
import { useTheme } from 'antd-style';
import { memo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Flexbox } from 'react-layout-kit';

import { useIsMobile } from '@/hooks/useIsMobile';
import { ModelSelectorError } from '@/types/message';
import { modelsServer } from '@/services/models';
import { useGlobalStore } from '@/store/global';
import { GlobalLLMProviderKey } from '@/types/settings/modelProvider';
import { currentSettings } from '@/store/global/slices/settings/selectors/settings';

interface FetchModelParams {
  provider: GlobalLLMProviderKey;
}

const ModelSelector = memo<FetchModelParams>(({ provider }) => {
  const { t } = useTranslation('setting');

  const [loading, setLoading] = useState(false);
  const [pass, setPass] = useState(false);

  const theme = useTheme();
  const [error, setError] = useState<ModelSelectorError | undefined>();

  const [setConfig, languageModel ] = useGlobalStore((s) => [
    s.setModelProviderConfig,
    currentSettings(s).languageModel,
  ]);

  const enable = languageModel[provider]?.enabled || false;

  // 过滤格式
  const filterModel = (data: any[] = []) => {
    return data.map((item) => {

      return {
        tokens: item?.tokens || 8000,
        displayName: item.displayName || item.id,
        functionCall:  false, // false 默认都不能用使用插件，chatchat 的插件还没弄
        ...item
      }
    })
  }

  const processProviderModels = () => {
    if(!enable) return

    setLoading(true);

    modelsServer.getModels(provider).then((data) => {
      if (data.error) {
        setError({ message: data.error, type: 500});
      } else {
        // 更新模型
        setConfig(provider, { models: filterModel(data.data) });

        setError(undefined);
        setPass(true);
      }

    }).finally(() => {
      setLoading(false);
    })
  }

  const isMobile = useIsMobile();

  return (
    <Flexbox align={isMobile ? 'flex-start' : 'flex-end'} gap={8}>
      <Flexbox align={'center'} direction={isMobile ? 'horizontal-reverse' : 'horizontal'} gap={12}>
        {pass && (
          <Flexbox gap={4} horizontal>
            <CheckCircleFilled
              style={{
                color: theme.colorSuccess,
              }}
            />
            {t('llm.selectorModel.pass')}
          </Flexbox>
        )}
        <Button loading={loading} onClick={processProviderModels}>
          {t('llm.selectorModel.button')}
        </Button>
      </Flexbox>
      {error && (
        <Flexbox gap={8} style={{ maxWidth: '600px', width: '100%' }}>
          <Alert
            banner
            extra={
              <Flexbox>
                <Highlighter copyButtonSize={'small'} language={'json'} type={'pure'}>
                  {JSON.stringify(error, null, 2)}
                </Highlighter>
              </Flexbox>
            }
            message={t(`response.${error.type}` as any, { ns: 'error' })}
            showIcon
            type={'error'}
          />
        </Flexbox>
      )}
    </Flexbox>
  );
});

export default ModelSelector;

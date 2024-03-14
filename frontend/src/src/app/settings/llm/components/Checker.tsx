import { CheckCircleFilled } from '@ant-design/icons';
import { Alert, Highlighter } from '@lobehub/ui';
import { Button } from 'antd';
import { useTheme } from 'antd-style';
import { memo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Flexbox } from 'react-layout-kit';

import { TraceNameMap } from '@/const/trace';
import { useIsMobile } from '@/hooks/useIsMobile';
import { chatService } from '@/services/chat';
import { ChatMessageError } from '@/types/message';

interface ConnectionCheckerProps {
  model: string;
  provider: string;
}

const Checker = memo<ConnectionCheckerProps>(({ model, provider }) => {
  const { t } = useTranslation('setting');

  const [loading, setLoading] = useState(false);
  const [pass, setPass] = useState(false);

  const theme = useTheme();
  const [error, setError] = useState<ChatMessageError | undefined>();

  const checkConnection = async () => {
    const data = await chatService.fetchPresetTaskResult({
      onError: (_, rawError) => {
        setError(rawError);
        setPass(false);
      },
      onLoadingChange: (loading) => {
        setLoading(loading);
      },
      params: {
        messages: [
          {
            content: '你好',
            role: 'user',
          },
        ],
        model,
        provider,
      },
      trace: {
        sessionId: `connection:${provider}`,
        topicId: model,
        traceName: TraceNameMap.ConnectivityChecker,
      },
    });

    if (data) {
      setError(undefined);
      setPass(true);
    }
  };
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
            {t('llm.checker.pass')}
          </Flexbox>
        )}
        <Button loading={loading} onClick={checkConnection}>
          {t('llm.checker.button')}
        </Button>
      </Flexbox>
      {error && (
        <Flexbox gap={8} style={{ maxWidth: '600px', width: '100%' }}>
          <Alert
            banner
            extra={
              <Flexbox>
                <Highlighter copyButtonSize={'small'} language={'json'} type={'pure'}>
                  {JSON.stringify(error.body || error, null, 2)}
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

export default Checker;

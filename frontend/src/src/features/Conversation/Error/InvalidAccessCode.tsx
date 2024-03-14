import { Icon } from '@lobehub/ui';
import { Segmented } from 'antd';
import { SegmentedLabeledOption } from 'antd/es/segmented';
import { AsteriskSquare, KeySquare, ScanFace } from 'lucide-react';
import { memo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Flexbox } from 'react-layout-kit';

import { useGlobalStore } from '@/store/global';
import { commonSelectors } from '@/store/global/selectors';

import APIKeyForm from './APIKeyForm';
import AccessCodeForm from './AccessCodeForm';
import OAuthForm from './OAuthForm';
import { ErrorActionContainer } from './style';

enum Tab {
  Api = 'api',
  Oauth = 'oauth',
  Password = 'password',
}

interface InvalidAccessCodeProps {
  id: string;
  provider?: string;
}

const InvalidAccessCode = memo<InvalidAccessCodeProps>(({ id, provider }) => {
  const { t } = useTranslation('error');
  const isEnabledOAuth = useGlobalStore(commonSelectors.enabledOAuthSSO);
  const defaultTab = isEnabledOAuth ? Tab.Oauth : Tab.Password;
  const [mode, setMode] = useState<Tab>(defaultTab);

  return (
    <ErrorActionContainer>
      <Segmented
        block
        onChange={(value) => setMode(value as Tab)}
        options={
          [
            isEnabledOAuth
              ? {
                  icon: <Icon icon={ScanFace} />,
                  label: t('oauth', { ns: 'common' }),
                  value: Tab.Oauth,
                }
              : undefined,
            {
              icon: <Icon icon={AsteriskSquare} />,
              label: t('unlock.tabs.password'),
              value: Tab.Password,
            },
            { icon: <Icon icon={KeySquare} />, label: t('unlock.tabs.apiKey'), value: Tab.Api },
          ].filter(Boolean) as SegmentedLabeledOption[]
        }
        style={{ width: '100%' }}
        value={mode}
      />
      <Flexbox gap={24}>
        {mode === Tab.Password && <AccessCodeForm id={id} />}
        {mode === Tab.Api && <APIKeyForm id={id} provider={provider} />}
        {isEnabledOAuth && mode === Tab.Oauth && <OAuthForm id={id} />}
      </Flexbox>
    </ErrorActionContainer>
  );
});

export default InvalidAccessCode;

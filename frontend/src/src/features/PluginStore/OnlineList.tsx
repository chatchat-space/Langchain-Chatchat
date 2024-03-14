import { Icon, SearchBar } from '@lobehub/ui';
import { Empty } from 'antd';
import { useResponsive } from 'antd-style';
import isEqual from 'fast-deep-equal';
import { ServerCrash } from 'lucide-react';
import { memo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Center, Flexbox } from 'react-layout-kit';

import AddPluginButton from '@/features/PluginStore/AddPluginButton';
import { useToolStore } from '@/store/tool';
import { pluginSelectors, pluginStoreSelectors } from '@/store/tool/selectors';

import Loading from './Loading';
import PluginItem from './PluginItem';

export const OnlineList = memo(() => {
  const { t } = useTranslation('plugin');
  const [keywords, setKeywords] = useState<string>();
  const { mobile } = useResponsive();
  const pluginStoreList = useToolStore((s) => {
    const custom = pluginSelectors.installedCustomPluginMetaList(s);
    const store = pluginStoreSelectors.onlinePluginStore(s);

    return [...custom, ...store];
  }, isEqual);

  const useFetchPluginList = useToolStore((s) => s.useFetchPluginStore);

  const { isLoading, error } = useFetchPluginList();

  const isEmpty = pluginStoreList.length === 0;

  return (
    <>
      <Flexbox align={'center'} gap={8} horizontal justify={'space-between'}>
        <Flexbox flex={1}>
          <SearchBar
            allowClear
            onChange={(e) => setKeywords(e.target.value)}
            placeholder={t('store.placeholder')}
            type={mobile ? 'block' : 'ghost'}
            value={keywords}
          />
        </Flexbox>
        <AddPluginButton />
      </Flexbox>

      {isLoading ? (
        <Loading />
      ) : isEmpty ? (
        <Center gap={12} padding={40}>
          {error ? (
            <>
              <Icon icon={ServerCrash} size={{ fontSize: 80 }} />
              {t('store.networkError')}
            </>
          ) : (
            <Empty description={t('store.empty')} image={Empty.PRESENTED_IMAGE_SIMPLE} />
          )}
        </Center>
      ) : (
        <Flexbox gap={24}>
          {pluginStoreList
            .filter((item) =>
              [item.meta?.title, item.meta?.description, item.author, ...(item.meta?.tags || [])]
                .filter(Boolean)
                .join('')
                .toLowerCase()
                .includes((keywords || '')?.toLowerCase()),
            )
            .map((item) => (
              <PluginItem key={item.identifier} {...item} />
            ))}
        </Flexbox>
      )}
    </>
  );
});

export default OnlineList;

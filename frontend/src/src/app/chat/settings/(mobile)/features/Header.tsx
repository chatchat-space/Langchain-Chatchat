import { MobileNavBar, MobileNavBarTitle } from '@lobehub/ui';
import { useRouter } from 'next/navigation';
import { memo } from 'react';
import { useTranslation } from 'react-i18next';

import HeaderContent from '@/app/chat/settings/features/HeaderContent';
import { pathString } from '@/utils/url';

const Header = memo(() => {
  const { t } = useTranslation('setting');
  const router = useRouter();

  return (
    <MobileNavBar
      center={<MobileNavBarTitle title={t('header.session')} />}
      onBackClick={() => router.push(pathString('/chat/mobile', { search: location.search }))}
      right={<HeaderContent />}
      showBackButton
    />
  );
});

export default Header;

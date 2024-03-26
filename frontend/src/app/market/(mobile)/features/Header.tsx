import { MobileNavBar } from '@lobehub/ui';
import { memo } from 'react';
import Logo from '@/components/Logo';
import ShareAgentButton from '../../features/ShareAgentButton';

const Header = memo(() => {
  return <MobileNavBar center={<Logo type={'text'} />} right={<ShareAgentButton mobile />} />;
});

export default Header;

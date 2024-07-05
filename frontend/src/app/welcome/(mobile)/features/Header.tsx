import { MobileNavBar } from '@lobehub/ui';
import { memo } from 'react';
import Logo from '@/components/Logo';

const Header = memo(() => <MobileNavBar center={<Logo type={'text'} />} />);

export default Header;

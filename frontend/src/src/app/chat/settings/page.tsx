import { isMobileDevice } from '@/utils/responsive';

import DesktopPage from './(desktop)';
import MobilePage from './(mobile)';

const Page = () => {
  const mobile = isMobileDevice();

  const Page = mobile ? MobilePage : DesktopPage;

  return <Page />;
};

export default Page;

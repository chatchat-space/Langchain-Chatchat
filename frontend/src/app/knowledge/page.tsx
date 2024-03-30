import DesktopPage from './(desktop)';

// import MobilePage from './(mobile)';
// import SessionHydration from './components/SessionHydration';
// import Migration from './features/Migration';

const Page = () => {
  // const mobile = isMobileDevice();

  // const Page = mobile ? MobilePage : DesktopPage;
  const Page = DesktopPage;

  return <Page />;
};

export default Page;

import { getAppConfig } from './app';
import { getProviderConfig } from './provider';

export const getServerConfig = () => {
  if (typeof process === 'undefined') {
    throw new Error('[Server Config] you are importing a server-only module outside of server');
  }

  const provider = getProviderConfig();
  const app = getAppConfig();

  return { ...provider, ...app };
};

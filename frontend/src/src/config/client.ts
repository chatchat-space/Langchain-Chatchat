/**
 * the client config is only used in Vercel deployment
 */

/* eslint-disable sort-keys-fix/sort-keys-fix , typescript-sort-keys/interface */

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_ANALYTICS_VERCEL?: string;
      NEXT_PUBLIC_VERCEL_DEBUG?: string;

      NEXT_PUBLIC_ANALYTICS_MIXPANEL?: string;
      NEXT_PUBLIC_MIXPANEL_PROJECT_TOKEN?: string;
      NEXT_PUBLIC_MIXPANEL_DEBUG?: string;

      NEXT_PUBLIC_ANALYTICS_PLAUSIBLE?: string;
      NEXT_PUBLIC_PLAUSIBLE_DOMAIN?: string;
      NEXT_PUBLIC_PLAUSIBLE_SCRIPT_BASE_URL?: string;

      NEXT_PUBLIC_ANALYTICS_POSTHOG: string;
      NEXT_PUBLIC_POSTHOG_KEY: string;
      NEXT_PUBLIC_POSTHOG_HOST: string;
      NEXT_PUBLIC_POSTHOG_DEBUG: string;

      NEXT_PUBLIC_ANALYTICS_UMAMI?: string;
      NEXT_PUBLIC_UMAMI_SCRIPT_URL?: string;
      NEXT_PUBLIC_UMAMI_WEBSITE_ID?: string;

      NEXT_PUBLIC_I18N_DEBUG: string;
      NEXT_PUBLIC_I18N_DEBUG_BROWSER: string;
      NEXT_PUBLIC_I18N_DEBUG_SERVER: string;

      NEXT_PUBLIC_DEVELOPER_DEBUG: string;

      NEXT_PUBLIC_LOBE_CHAT_DOCS: string;
    }
  }
}

export const getClientConfig = () => ({
  BASE_PATH: process.env.NEXT_PUBLIC_BASE_PATH || '',

  // docs
  LOBE_CHAT_DOCS: process.env.NEXT_PUBLIC_LOBE_CHAT_DOCS,

  // Vercel Analytics
  ANALYTICS_VERCEL: process.env.NEXT_PUBLIC_ANALYTICS_VERCEL === '1',
  VERCEL_DEBUG: process.env.NEXT_PUBLIC_VERCEL_DEBUG === '1',

  // Plausible Analytics
  ANALYTICS_PLAUSIBLE: process.env.NEXT_PUBLIC_ANALYTICS_PLAUSIBLE === '1',
  PLAUSIBLE_DOMAIN: process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN,
  PLAUSIBLE_SCRIPT_BASE_URL:
    process.env.NEXT_PUBLIC_PLAUSIBLE_SCRIPT_BASE_URL || 'https://plausible.io',

  // Posthog Analytics
  ANALYTICS_POSTHOG: process.env.NEXT_PUBLIC_ANALYTICS_POSTHOG === '1',
  POSTHOG_KEY: process.env.NEXT_PUBLIC_POSTHOG_KEY,
  POSTHOG_HOST: process.env.NEXT_PUBLIC_POSTHOG_HOST,
  POSTHOG_DEBUG: process.env.NEXT_PUBLIC_POSTHOG_DEBUG === '1',

  // Umami Analytics
  ANALYTICS_UMAMI: process.env.NEXT_PUBLIC_ANALYTICS_UMAMI === '1',
  UMAMI_SCRIPT_URL:
    process.env.NEXT_PUBLIC_UMAMI_SCRIPT_URL || 'https://analytics.umami.is/script.js',
  UMAMI_WEBSITE_ID: process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID,

  // i18n debug mode
  I18N_DEBUG: process.env.NEXT_PUBLIC_I18N_DEBUG === '1',
  I18N_DEBUG_BROWSER: process.env.NEXT_PUBLIC_I18N_DEBUG_BROWSER === '1',
  I18N_DEBUG_SERVER: process.env.NEXT_PUBLIC_I18N_DEBUG_SERVER === '1',

  // developer debug mode
  DEBUG_MODE: process.env.NEXT_PUBLIC_DEVELOPER_DEBUG === '1',
});

import { describe, expect, it, vi } from 'vitest';

import { getClientConfig } from '../client';

// 测试前重置 process.env
vi.stubGlobal('process', {
  ...process, // 保持原有的 process 对象
  env: { ...process.env }, // 克隆环境变量对象，以便修改
});

describe('getClientConfig', () => {
  it('should correctly reflect boolean values for analytics flags', () => {
    process.env.NEXT_PUBLIC_ANALYTICS_VERCEL = '1';
    process.env.NEXT_PUBLIC_VERCEL_DEBUG = '1';
    process.env.NEXT_PUBLIC_ANALYTICS_PLAUSIBLE = '1';
    process.env.NEXT_PUBLIC_ANALYTICS_POSTHOG = '1';
    process.env.NEXT_PUBLIC_POSTHOG_DEBUG = '1';
    process.env.NEXT_PUBLIC_I18N_DEBUG = '1';
    process.env.NEXT_PUBLIC_I18N_DEBUG_BROWSER = '1';
    process.env.NEXT_PUBLIC_I18N_DEBUG_SERVER = '1';

    const config = getClientConfig();
    expect(config.ANALYTICS_VERCEL).toBe(true);
    expect(config.VERCEL_DEBUG).toBe(true);
    expect(config.ANALYTICS_PLAUSIBLE).toBe(true);
    expect(config.ANALYTICS_POSTHOG).toBe(true);
    expect(config.POSTHOG_DEBUG).toBe(true);
    expect(config.I18N_DEBUG).toBe(true);
    expect(config.I18N_DEBUG_BROWSER).toBe(true);
    expect(config.I18N_DEBUG_SERVER).toBe(true);
  });

  it('should correctly handle falsy values for analytics flags', () => {
    process.env.NEXT_PUBLIC_ANALYTICS_VERCEL = '0';
    process.env.NEXT_PUBLIC_VERCEL_DEBUG = '0';
    process.env.NEXT_PUBLIC_ANALYTICS_PLAUSIBLE = '0';
    process.env.NEXT_PUBLIC_ANALYTICS_POSTHOG = '0';
    process.env.NEXT_PUBLIC_POSTHOG_DEBUG = '0';
    process.env.NEXT_PUBLIC_I18N_DEBUG = '0';
    process.env.NEXT_PUBLIC_I18N_DEBUG_BROWSER = '0';
    process.env.NEXT_PUBLIC_I18N_DEBUG_SERVER = '0';

    const config = getClientConfig();
    expect(config.ANALYTICS_VERCEL).toBe(false);
    expect(config.VERCEL_DEBUG).toBe(false);
    expect(config.ANALYTICS_PLAUSIBLE).toBe(false);
    expect(config.ANALYTICS_POSTHOG).toBe(false);
    expect(config.POSTHOG_DEBUG).toBe(false);
    expect(config.I18N_DEBUG).toBe(false);
    expect(config.I18N_DEBUG_BROWSER).toBe(false);
    expect(config.I18N_DEBUG_SERVER).toBe(false);
  });
});

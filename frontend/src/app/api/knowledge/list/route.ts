import { NextResponse } from 'next/server';

import { getServerConfig } from '@/config/server';

export const dynamic = 'force-dynamic';

export const GET = async () => {
  try {
    const { KNOWLEDGE_PROXY_URL } = getServerConfig();
    console.log('KNOWLEDGE_PROXY_URL:', KNOWLEDGE_PROXY_URL);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000); // 3 秒超时

    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/list_knowledge_bases`, {
      signal: controller.signal,
    });
    clearTimeout(timeout);
    return fetchRes;
  } catch (err) {
    console.error('API Error:', err);
    return NextResponse.json(
      { error: 'API failure', message: err instanceof Error ? err.message : String(err) },
      { status: 500 },
    );
  }
};

import { NextResponse } from 'next/server';

import { getServerConfig } from '@/config/server';

export const GET = async (request: Request) => {
  const { KNOWLEDGE_PROXY_URL } = getServerConfig(); // ✅ 延迟调用

  try {
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/list_knowledge_bases`);

    if (!fetchRes.ok) {
      return NextResponse.json({ error: 'Failed to fetch' }, { status: fetchRes.status });
    }

    const data = await fetchRes.json();
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { error: 'Fetch failed', detail: (err as Error).message },
      { status: 500 },
    );
  }
};

import { getServerConfig } from '@/config/server';
const { KNOWLEDGE_PROXY_URL } = getServerConfig();

export const GET = async (request: Request) => {
    const searchParams = new URL(request.url).searchParams;
    const knowledge_base_name = searchParams.get('knowledge_base_name') as string;
    const file_name = searchParams.get('file_name') as string;
    const preview = searchParams.get('preview') as string;
 
    const queryString = new URLSearchParams({ knowledge_base_name, file_name, preview }).toString();
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/download_doc?${queryString}`);
    return fetchRes;
};

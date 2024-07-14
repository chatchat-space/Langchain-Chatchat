import { getServerConfig } from '@/config/server'; 
const { KNOWLEDGE_PROXY_URL } = getServerConfig();
export const GET = async (request: Request) => {   
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/list_knowledge_bases`);  
    return fetchRes;
};

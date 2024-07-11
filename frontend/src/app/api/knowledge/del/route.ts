
import { getServerConfig } from '@/config/server'; 
const { KNOWLEDGE_PROXY_URL } = getServerConfig();

export const POST = async (request: Request) => {
    const params = await request.text();  
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/delete_knowledge_base`, {
        body: params,
        headers: {
            'Content-Type': 'application/json',
        },
        method: 'POST',
    });  
    return fetchRes
};

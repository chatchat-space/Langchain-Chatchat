import { getServerConfig } from '@/config/server'; 
const { KNOWLEDGE_PROXY_URL } = getServerConfig(); 
export const POST = async (request: Request) => {  
    const params = await request.json(); 
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/delete_docs`, {
        body: JSON.stringify(params),
        headers: {
            'Content-Type': 'application/json',
        },
        method: 'POST',
    });  
    return fetchRes
};

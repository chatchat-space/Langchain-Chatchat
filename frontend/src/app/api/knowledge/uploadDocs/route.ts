
import { getServerConfig } from '@/config/server'; 
const { KNOWLEDGE_PROXY_URL } = getServerConfig();

export const POST = async (request: Request) => {
    const formData = await request.formData(); 
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/upload_docs`, {
        body: formData, 
        method: 'POST',
    });  
    return fetchRes
};

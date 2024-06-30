
import { getServerConfig } from '@/config/server';
const { KNOWLEDGE_PROXY_URL } = getServerConfig();

export const POST = async (request: Request) => {
    const formData = await request.json(); 
    const fetchRes = await fetch(`${KNOWLEDGE_PROXY_URL}/upload_docs`, {
        body: JSON.stringify(formData),
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return fetchRes
};

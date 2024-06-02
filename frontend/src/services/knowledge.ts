
import { KnowledgeList, KnowledgeFormFields, Reseponse } from '@/types/knowledge';

import { API_ENDPOINTS } from './_url';

class KnowledgeService {
    getList = async (): Promise<Reseponse<KnowledgeList>> => { 
        const res = await fetch(`${API_ENDPOINTS.knowledgeList}`);
        const data = await res.json();
        return data;
    };

    add = async (formValues: KnowledgeFormFields) => { 
        const res = await fetch(`${API_ENDPOINTS.knowledgeAdd}`, {
            body: JSON.stringify(formValues),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    };

    del = async (name: string) => { 
        const res = await fetch(`${API_ENDPOINTS.knowledgeDel}`, {
            body: JSON.stringify(name),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    };
}

export const knowledgeService = new KnowledgeService();


import type {
    KnowledgeList, KnowledgeFormFields, Reseponse,
    KnowledgeFilesList, KnowledgeDelDocsParams, KnowledgeDelDocsRes,
    KnowledgeRebuildVectorParams, 
    ReAddVectorDBParams, ReAddVectorDBRes,
    KnowledgeSearchDocsParams, KnowledgeSearchDocsList, KnowledgeUpdateDocsParams
} from '@/types/knowledge';

import { fetchSSE, FetchSSEOptions } from '@/utils/fetch';
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
    update = async (formValues: Partial<KnowledgeFormFields>) => {
        const res = await fetch(`${API_ENDPOINTS.knowledgeUpdate}`, {
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

    getFilesList = (name: string): () => Promise<Reseponse<KnowledgeFilesList>> => {
        const queryString = new URLSearchParams({
            knowledge_base_name: name
        }).toString();
        return async () => {
            const res = await fetch(`${API_ENDPOINTS.knowledgeFilesList}?${queryString}`);
            const data = await res.json();
            return data;
        }
    };

    uploadDocs = async (formData: FormData): Promise<Reseponse<{}>> => {
        const res = await fetch(`${API_ENDPOINTS.knowledgeUploadDocs}`, {
            body: formData,
            method: 'POST',
        });
        return res.json();
    };

    delInknowledgeDB = async (params: KnowledgeDelDocsParams): Promise<Reseponse<KnowledgeDelDocsRes>> => {
        const res = await fetch(`${API_ENDPOINTS.knowledgeDelInknowledgeDB}`, {
            body: JSON.stringify({
                ...params,
            }),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    };

    rebuildVectorDB = async (params: KnowledgeRebuildVectorParams, opts:
        { onFinish: FetchSSEOptions["onFinish"]; onMessageHandle: FetchSSEOptions["onMessageHandle"] }
    ) => {
        const { onFinish, onMessageHandle } = opts;
        fetchSSE(async () => await fetch(`${API_ENDPOINTS.knowledgeRebuildVectorDB}`, {
            body: JSON.stringify({
                ...params,
            }),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST'
        }), {
            onErrorHandle: (error) => {
                throw new Error('请求错误：' + error);
            },
            onFinish,
            onMessageHandle
        })
    };

    delVectorDocs = async (params: KnowledgeDelDocsParams): Promise<Reseponse<KnowledgeDelDocsRes>> => {
        const res = await fetch(`${API_ENDPOINTS.knowledgeDelVectorDB}`, {
            body: JSON.stringify({
                ...params,
            }),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    };
 
    downloadDocs = async (kbName: string, docName: string): Promise<void> => {
        const queryString = new URLSearchParams({
            knowledge_base_name: kbName,
            file_name: docName,
            preview: 'false'
        }).toString();
        const url = `${API_ENDPOINTS.knowledgeDownloadDocs}?${queryString}`;
        window.open(url, docName); 
    }; 
    reAddVectorDB = async (params: ReAddVectorDBParams): Promise<Reseponse<ReAddVectorDBRes>> => {
        const res = await fetch(`${API_ENDPOINTS.knowledgeReAddVectorDB}`, {
            body: JSON.stringify({
                ...params,
            }),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    };
    // searchDocs = async (params: KnowledgeSearchDocsParams): Promise<Reseponse<KnowledgeSearchDocsList>> => {
    searchDocs = async (params: KnowledgeSearchDocsParams): Promise<KnowledgeSearchDocsList> => {
        const res = await fetch(`${API_ENDPOINTS.knowledgeSearchDocs}`, {
            body: JSON.stringify({
                ...params,
            }),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    }; 
    updateDocs = async (params: KnowledgeUpdateDocsParams): Promise<Reseponse<{}>> => {
        const res = await fetch(`${API_ENDPOINTS.updateDocsContent}`, {
            body: JSON.stringify({
                ...params,
            }),
            headers: {
                'Content-Type': 'application/json',
            },
            method: 'POST',
        });
        return res.json();
    }; 
}

export const knowledgeService = new KnowledgeService();

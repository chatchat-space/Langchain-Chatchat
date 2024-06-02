export interface Reseponse <T> { code: number; msg: string; data: T }

export interface KnowledgeFormFields {
    knowledge_base_name: string;
    vector_store_type: string;
    kb_info?: string;
    embed_model: string;
}

export interface KnowledgeListItemFields extends KnowledgeFormFields { }

export type KnowledgeList = KnowledgeListItemFields[];

export interface Reseponse<T> { code: number; msg: string; data: T }


// create Knowledge fields
export interface KnowledgeFormFields {
    knowledge_base_name: string;
    vector_store_type: string;
    kb_info?: string;
    embed_model: string;
}

// Knowledge base list
export interface KnowledgeListFields {
    "id": number;
    "kb_name": string;
    "kb_info": string;
    "vs_type": string;
    "embed_model": string;
    "file_count": number;
    "create_time": string;
} 
export type KnowledgeList = KnowledgeListFields[];

// Knowledge base file list
export type KnowledgeFilesFields = string;
export type KnowledgeFilesList = KnowledgeFilesFields[];

// Example Delete parameters of the knowledge base file
export interface KnowledgeDelDocsParams {
    knowledge_base_name: string;
    file_names: string[];
    delete_content: boolean;
    not_refresh_vs_cache: boolean;
} 
export interface KnowledgeDelDocsRes {
    knowledge_base_name: string;
    file_names: string[];
    delete_content: boolean;
    not_refresh_vs_cache: boolean;
} 



// Rebuild the vector library
export interface KnowledgeRebuildVectorParams {
    "knowledge_base_name": string;
    "allow_empty_kb": boolean;
    "vs_type": string;
    "embed_model": string
    "chunk_size": number;
    "chunk_overlap": number;
    "zh_title_enhance": boolean;
    "not_refresh_vs_cache": boolean;
} 
export interface KnowledgeRebuildVectorRes { } 



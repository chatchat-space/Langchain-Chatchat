export interface Reseponse<T> {
  code: number;
  data: T;
  msg: string;
}

// create Knowledge fields
export interface KnowledgeFormFields {
  embed_model?: string;
  kb_info?: string;
  knowledge_base_name: string;
  metadata?: any;
  type?: string;
  vector_store_type?: string;
}

// Knowledge base list
export interface KnowledgeListFields {
  create_time: string;
  embed_model: string;
  file_count: number;
  id: number;
  kb_info: string;
  kb_name: string;
  vs_type: string;
}
export type KnowledgeList = KnowledgeListFields[];

// Knowledge base file list
export type KnowledgeFilesFields = {
  No: number;
  docs_count: number;
  document_loader: string;
  file_ext: string;
  file_name: string;
  file_version: number;
  in_db: boolean;
  in_folder: boolean;
  kb_name: string;
  text_splitter: string;
};
export type KnowledgeFilesList = KnowledgeFilesFields[];

// Example Delete parameters of the knowledge base file
export interface KnowledgeDelDocsParams {
  delete_content: boolean;
  file_names: string[];
  knowledge_base_name: string;
  not_refresh_vs_cache: boolean;
}
export interface KnowledgeDelDocsRes {}

// upload docs
export interface KnowledgeUplodDocsParams {
  chunk_overlap?: string;
  chunk_size?: string;
  docs?: { file_name: { metadata?: string, page_content: string; type?: string; }[] };
  docsnot_refresh_vs_cache?: string;
  files: File[];
  knowledge_base_name: string;
  override?: boolean;
  to_vector_store?: string;
  zh_title_enhance?: string;
}
export interface KnowledgeUplodDocsRes {}

export interface KnowledgeUpdateDocsParams {
  chunk_overlap?: number;
  chunk_size?: number;
  docs?:
    | string
    | { [file_name: string]: { metadata?: string, page_content: string; type?: string; }[] };
  file_names: string[];
  knowledge_base_name: string;
  not_refresh_vs_cache?: boolean;
  override_custom_docs?: boolean;
  to_vector_store?: boolean;
  zh_title_enhance?: boolean;
  // docs?: string;
}

// re add docs
export interface ReAddVectorDBParams {
  chunk_overlap: number;
  chunk_size: number;
  docs: string;
  file_names: string[];
  knowledge_base_name: string;
  not_refresh_vs_cache: boolean;
  override_custom_docs: boolean;
  zh_title_enhance: boolean;
}
export interface ReAddVectorDBRes {}

// Rebuild the vector library
export interface KnowledgeRebuildVectorParams {
  allow_empty_kb: boolean;
  chunk_overlap: number;
  chunk_size: number;
  embed_model: string;
  knowledge_base_name: string;
  not_refresh_vs_cache: boolean;
  vs_type: string;
  zh_title_enhance: boolean;
}
export interface KnowledgeRebuildVectorRes {}

// Knowledge file content list
export interface KnowledgeSearchDocsParams {
  file_name: string;
  knowledge_base_name: string;
  metadata?: Record<string, string>;
  query?: string;
  score_threshold?: number;
  top_k?: number;
}

export interface KnowledgeSearchDocsListItem {
  id?: number;
  metadata?: string;
  page_content: string;
  type?: string;
}
export type KnowledgeSearchDocsList = KnowledgeSearchDocsListItem[];

from server.knowledge_base.utils import (get_vs_path, get_kb_path, get_doc_path)

SUPPORTED_VS_TYPES = ["faiss", "milvus"]


class KnowledgeBase:
    def __init__(self,
                 knowledge_base_name: str,
                 vector_store_type: str,
                 ):
        self.kb_name = knowledge_base_name
        if vector_store_type not in SUPPORTED_VS_TYPES:
            raise ValueError(f"暂未支持向量库类型 {vector_store_type}")
        self.vs_type = vector_store_type
        self.kb_path = get_kb_path(self.kb_name)
        self.doc_path = get_doc_path(self.kb_name)
        if self.vs_type in ["faiss"]:
            self.vs_path = get_vs_path(self.kb_name)
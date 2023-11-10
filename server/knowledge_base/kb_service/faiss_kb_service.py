import os
import shutil

from configs import (
    KB_ROOT_PATH,
    SCORE_THRESHOLD,
    logger, log_verbose,
)
from server.knowledge_base.kb_service.base import KBService, SupportedVSType
from server.knowledge_base.kb_cache.faiss_cache import kb_faiss_pool, ThreadSafeFaiss
from server.knowledge_base.utils import KnowledgeFile
from langchain.embeddings.base import Embeddings
from typing import List, Dict, Optional
from langchain.docstore.document import Document
from server.utils import torch_gc


class FaissKBService(KBService):
    vs_path: str
    kb_path: str
    vector_name: str = "vector_store"

    def vs_type(self) -> str:
        return SupportedVSType.FAISS

    def get_vs_path(self):
        return os.path.join(self.get_kb_path(), self.vector_name)

    def get_kb_path(self):
        return os.path.join(KB_ROOT_PATH, self.kb_name)

    def load_vector_store(self) -> ThreadSafeFaiss:
        return kb_faiss_pool.load_vector_store(kb_name=self.kb_name,
                                               vector_name=self.vector_name,
                                               embed_model=self.embed_model)

    def save_vector_store(self):
        self.load_vector_store().save(self.vs_path)

    def get_doc_by_id(self, id: str) -> Optional[Document]:
        with self.load_vector_store().acquire() as vs:
            return vs.docstore._dict.get(id)

    def do_init(self):
        self.kb_path = self.get_kb_path()
        self.vs_path = self.get_vs_path()

    def do_create_kb(self):
        if not os.path.exists(self.vs_path):
            os.makedirs(self.vs_path)
        self.load_vector_store()

    def do_drop_kb(self):
        self.clear_vs()
        shutil.rmtree(self.kb_path)

    def do_search(self,
                  query: str,
                  top_k: int,
                  score_threshold: float = SCORE_THRESHOLD,
                  embeddings: Embeddings = None,
                  ) -> List[Document]:
        with self.load_vector_store().acquire() as vs:
            docs = vs.similarity_search_with_score(query, k=top_k, score_threshold=score_threshold)
        return docs

    def do_add_doc(self,
                   docs: List[Document],
                   **kwargs,
                   ) -> List[Dict]:
        with self.load_vector_store().acquire() as vs:
            ids = vs.add_documents(docs)
            if not kwargs.get("not_refresh_vs_cache"):
                vs.save_local(self.vs_path)
        doc_infos = [{"id": id, "metadata": doc.metadata} for id, doc in zip(ids, docs)]
        torch_gc()
        return doc_infos

    def do_delete_doc(self,
                      kb_file: KnowledgeFile,
                      **kwargs):
        with self.load_vector_store().acquire() as vs:
            ids = [k for k, v in vs.docstore._dict.items() if v.metadata.get("source") == kb_file.filepath]
            if len(ids) > 0:
                vs.delete(ids)
            if not kwargs.get("not_refresh_vs_cache"):
                vs.save_local(self.vs_path)
        return ids

    def do_clear_vs(self):
        with kb_faiss_pool.atomic:
            kb_faiss_pool.pop((self.kb_name, self.vector_name))
        shutil.rmtree(self.vs_path)
        os.makedirs(self.vs_path)

    def exist_doc(self, file_name: str):
        if super().exist_doc(file_name):
            return "in_db"

        content_path = os.path.join(self.kb_path, "content")
        if os.path.isfile(os.path.join(content_path, file_name)):
            return "in_folder"
        else:
            return False


if __name__ == '__main__':
    faissService = FaissKBService("test")
    faissService.add_doc(KnowledgeFile("README.md", "test"))
    faissService.delete_doc(KnowledgeFile("README.md", "test"))
    faissService.do_drop_kb()
    print(faissService.search_docs("如何启动api服务"))

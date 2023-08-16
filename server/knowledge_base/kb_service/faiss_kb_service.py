import os
import shutil

from configs.model_config import (
    KB_ROOT_PATH,
    CACHED_VS_NUM,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    SCORE_THRESHOLD
)
from server.knowledge_base.kb_service.base import KBService, SupportedVSType
from functools import lru_cache
from server.knowledge_base.utils import get_vs_path, load_embeddings, KnowledgeFile
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from typing import List
from langchain.docstore.document import Document
from server.utils import torch_gc


# make HuggingFaceEmbeddings hashable
def _embeddings_hash(self):
    return hash(self.model_name)


HuggingFaceEmbeddings.__hash__ = _embeddings_hash

_VECTOR_STORE_TICKS = {}


@lru_cache(CACHED_VS_NUM)
def load_vector_store(
        knowledge_base_name: str,
        embed_model: str = EMBEDDING_MODEL,
        embed_device: str = EMBEDDING_DEVICE,
        embeddings: Embeddings = None,
        tick: int = 0,  # tick will be changed by upload_doc etc. and make cache refreshed.
):
    print(f"loading vector store in '{knowledge_base_name}'.")
    vs_path = get_vs_path(knowledge_base_name)
    if embeddings is None:
        embeddings = load_embeddings(embed_model, embed_device)
    search_index = FAISS.load_local(vs_path, embeddings, normalize_L2=True)
    return search_index


def refresh_vs_cache(kb_name: str):
    """
    make vector store cache refreshed when next loading
    """
    _VECTOR_STORE_TICKS[kb_name] = _VECTOR_STORE_TICKS.get(kb_name, 0) + 1


class FaissKBService(KBService):
    vs_path: str
    kb_path: str

    def vs_type(self) -> str:
        return SupportedVSType.FAISS

    @staticmethod
    def get_vs_path(knowledge_base_name: str):
        return os.path.join(FaissKBService.get_kb_path(knowledge_base_name), "vector_store")

    @staticmethod
    def get_kb_path(knowledge_base_name: str):
        return os.path.join(KB_ROOT_PATH, knowledge_base_name)

    def do_init(self):
        self.kb_path = FaissKBService.get_kb_path(self.kb_name)
        self.vs_path = FaissKBService.get_vs_path(self.kb_name)

    def do_create_kb(self):
        if not os.path.exists(self.vs_path):
            os.makedirs(self.vs_path)

    def do_drop_kb(self):
        shutil.rmtree(self.kb_path)

    def do_search(self,
                  query: str,
                  top_k: int,
                  score_threshold: float = SCORE_THRESHOLD,
                  embeddings: Embeddings = None,
                  ) -> List[Document]:
        search_index = load_vector_store(self.kb_name,
                                         embeddings=embeddings,
                                         tick=_VECTOR_STORE_TICKS.get(self.kb_name))
        docs = search_index.similarity_search_with_score(query, k=top_k, score_threshold=score_threshold)
        return docs

    def do_add_doc(self,
                   docs: List[Document],
                   embeddings: Embeddings,
                   ):
        if os.path.exists(self.vs_path) and "index.faiss" in os.listdir(self.vs_path):
            vector_store = FAISS.load_local(self.vs_path, embeddings, normalize_L2=True)
            vector_store.add_documents(docs)
            torch_gc()
        else:
            if not os.path.exists(self.vs_path):
                os.makedirs(self.vs_path)
            vector_store = FAISS.from_documents(
                docs, embeddings, normalize_L2=True)  # docs 为Document列表
            torch_gc()
        vector_store.save_local(self.vs_path)
        refresh_vs_cache(self.kb_name)

    def do_delete_doc(self,
                      kb_file: KnowledgeFile):
        embeddings = self._load_embeddings()
        if os.path.exists(self.vs_path) and "index.faiss" in os.listdir(self.vs_path):
            vector_store = FAISS.load_local(self.vs_path, embeddings, normalize_L2=True)
            ids = [k for k, v in vector_store.docstore._dict.items() if v.metadata["source"] == kb_file.filepath]
            if len(ids) == 0:
                return None
            vector_store.delete(ids)
            vector_store.save_local(self.vs_path)
            refresh_vs_cache(self.kb_name)
            return True
        else:
            return None

    def do_clear_vs(self):
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

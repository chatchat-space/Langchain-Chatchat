from abc import ABC, abstractmethod

import os
from functools import lru_cache

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document

from server.db.repository.knowledge_base_repository import add_kb_to_db, delete_kb_from_db, list_kbs_from_db, kb_exists
from server.db.repository.knowledge_file_repository import add_doc_to_db, delete_file_from_db, doc_exists, \
    list_docs_from_db
from configs.model_config import (DB_ROOT_PATH, kbs_config, VECTOR_SEARCH_TOP_K,
                                  embedding_model_dict, EMBEDDING_DEVICE, EMBEDDING_MODEL)
from server.knowledge_base.utils import (get_kb_path, get_doc_path, KnowledgeFile)
from typing import List


class SupportedVSType:
    FAISS = 'faiss'
    MILVUS = 'milvus'
    DEFAULT = 'default'


def list_docs_from_folder(kb_name: str):
    doc_path = get_doc_path(kb_name)
    return [file for file in os.listdir(doc_path)
            if os.path.isfile(os.path.join(doc_path, file))]


@lru_cache(1)
def load_embeddings(model: str, device: str):
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[model],
                                       model_kwargs={'device': device})
    return embeddings


class KBService(ABC):

    def __init__(self,
                 knowledge_base_name: str,
                 embed_model: str = EMBEDDING_MODEL,
                 ):
        self.kb_name = knowledge_base_name
        self.embed_model = embed_model
        self.kb_path = get_kb_path(self.kb_name)
        self.doc_path = get_doc_path(self.kb_name)
        self.do_init()

    def create_kb(self):
        """
        创建知识库
        """
        if not os.path.exists(self.doc_path):
            os.makedirs(self.doc_path)
            self.do_create_kb()
        status = add_kb_to_db(self.kb_name, self.vs_type(), self.embed_model)
        return status

    def clear_vs(self):
        """
        用知识库中已上传文件重建向量库
        """
        self.do_clear_vs()

    def drop_kb(self):
        """
        删除知识库
        """
        self.do_drop_kb()
        status = delete_kb_from_db(self.kb_name)
        return status

    def add_doc(self, kb_file: KnowledgeFile):
        """
        向知识库添加文件
        """
        docs = kb_file.file2text()
        embeddings = load_embeddings(self.embed_model, EMBEDDING_DEVICE)
        self.do_add_doc(docs, embeddings)
        status = add_doc_to_db(kb_file)
        return status

    def delete_doc(self, kb_file: KnowledgeFile):
        """
        从知识库删除文件
        """
        if os.path.exists(kb_file.filepath):
            os.remove(kb_file.filepath)
        self.do_delete_doc(kb_file)
        status = delete_file_from_db(kb_file)
        return status

    def exist_doc(self, file_name: str):
        return doc_exists(KnowledgeFile(knowledge_base_name=self.kb_name,
                                        filename=file_name))

    def list_docs(self):
        return list_docs_from_db(self.kb_name)

    def search_docs(self,
                    query: str,
                    top_k: int = VECTOR_SEARCH_TOP_K,
                    embedding_device: str = EMBEDDING_DEVICE, ):
        embeddings = load_embeddings(self.embed_model, embedding_device)
        docs = self.do_search(query, top_k, embeddings)
        return docs

    @abstractmethod
    def do_create_kb(self):
        """
        创建知识库子类实自己逻辑
        """
        pass

    @staticmethod
    def list_kbs_type():
        return list(kbs_config.keys())

    @classmethod
    def list_kbs(cls):
        return list_kbs_from_db()

    @classmethod
    def exists(cls,
               knowledge_base_name: str):
        return kb_exists(knowledge_base_name)

    @abstractmethod
    def vs_type(self) -> str:
        pass

    @abstractmethod
    def do_init(self):
        pass

    @abstractmethod
    def do_drop_kb(self):
        """
        删除知识库子类实自己逻辑
        """
        pass

    @abstractmethod
    def do_search(self,
                  query: str,
                  top_k: int,
                  embeddings: Embeddings,
                  ) -> List[Document]:
        """
        搜索知识库子类实自己逻辑
        """
        pass

    @abstractmethod
    def do_add_doc(self,
                   docs: List[Document],
                   embeddings: Embeddings):
        """
        向知识库添加文档子类实自己逻辑
        """
        pass

    @abstractmethod
    def do_delete_doc(self,
                      kb_file: KnowledgeFile):
        """
        从知识库删除文档子类实自己逻辑
        """
        pass

    @abstractmethod
    def do_clear_vs(self):
        """
        从知识库删除全部向量子类实自己逻辑
        """
        pass

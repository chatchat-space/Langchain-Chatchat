from abc import ABC, abstractmethod

import os

from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from server.db.repository.knowledge_base_repository import (
    add_kb_to_db, delete_kb_from_db, list_kbs_from_db, kb_exists,
    load_kb_from_db, get_kb_detail,
)
from server.db.repository.knowledge_file_repository import (
    add_doc_to_db, delete_file_from_db, delete_files_from_db, doc_exists,
    list_docs_from_db, get_file_detail, delete_file_from_db
)

from configs.model_config import (kbs_config, VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD,
                                  EMBEDDING_DEVICE, EMBEDDING_MODEL)
from server.knowledge_base.utils import (
    get_kb_path, get_doc_path, load_embeddings, KnowledgeFile,
    list_kbs_from_folder, list_docs_from_folder,
)
from typing import List, Union, Dict


class SupportedVSType:
    FAISS = 'faiss'
    MILVUS = 'milvus'
    DEFAULT = 'default'
    PG = 'pg'


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

    def _load_embeddings(self, embed_device: str = EMBEDDING_DEVICE) -> Embeddings:
        return load_embeddings(self.embed_model, embed_device)

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
        删除向量库中所有内容
        """
        self.do_clear_vs()
        status = delete_files_from_db(self.kb_name)
        return status


    def drop_kb(self):
        """
        删除知识库
        """
        self.do_drop_kb()
        status = delete_kb_from_db(self.kb_name)
        return status

    def add_doc(self, kb_file: KnowledgeFile, **kwargs):
        """
        向知识库添加文件
        """
        docs = kb_file.file2text()
        if docs:
            self.delete_doc(kb_file)
            embeddings = self._load_embeddings()
            self.do_add_doc(docs, embeddings, **kwargs)
            status = add_doc_to_db(kb_file)
        else:
            status = False
        return status

    def delete_doc(self, kb_file: KnowledgeFile, delete_content: bool = False, **kwargs):
        """
        从知识库删除文件
        """
        self.do_delete_doc(kb_file, **kwargs)
        status = delete_file_from_db(kb_file)
        if delete_content and os.path.exists(kb_file.filepath):
            os.remove(kb_file.filepath)
        return status

    def update_doc(self, kb_file: KnowledgeFile, **kwargs):
        """
        使用content中的文件更新向量库
        """
        if os.path.exists(kb_file.filepath):
            self.delete_doc(kb_file, **kwargs)
            return self.add_doc(kb_file, **kwargs)
        
    def exist_doc(self, file_name: str):
        return doc_exists(KnowledgeFile(knowledge_base_name=self.kb_name,
                                        filename=file_name))

    def list_docs(self):
        return list_docs_from_db(self.kb_name)

    def search_docs(self,
                    query: str,
                    top_k: int = VECTOR_SEARCH_TOP_K,
                    score_threshold: float = SCORE_THRESHOLD,
                    ):
        embeddings = self._load_embeddings()
        docs = self.do_search(query, top_k, score_threshold, embeddings)
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

    def exists(self, kb_name: str = None):
        kb_name = kb_name or self.kb_name
        return kb_exists(kb_name)

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
                  score_threshold: float,
                  embeddings: Embeddings,
                  ) -> List[Document]:
        """
        搜索知识库子类实自己逻辑
        """
        pass

    @abstractmethod
    def do_add_doc(self,
                   docs: List[Document],
                   embeddings: Embeddings,
                   ):
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


class KBServiceFactory:

    @staticmethod
    def get_service(kb_name: str,
                    vector_store_type: Union[str, SupportedVSType],
                    embed_model: str = EMBEDDING_MODEL,
                    ) -> KBService:
        if isinstance(vector_store_type, str):
            vector_store_type = getattr(SupportedVSType, vector_store_type.upper())
        if SupportedVSType.FAISS == vector_store_type:
            from server.knowledge_base.kb_service.faiss_kb_service import FaissKBService
            return FaissKBService(kb_name, embed_model=embed_model)
        if SupportedVSType.PG == vector_store_type:
            from server.knowledge_base.kb_service.pg_kb_service import PGKBService
            return PGKBService(kb_name, embed_model=embed_model)
        elif SupportedVSType.MILVUS == vector_store_type:
            from server.knowledge_base.kb_service.milvus_kb_service import MilvusKBService
            return MilvusKBService(kb_name, embed_model=embed_model) # other milvus parameters are set in model_config.kbs_config
        elif SupportedVSType.DEFAULT == vector_store_type: # kb_exists of default kbservice is False, to make validation easier.
            from server.knowledge_base.kb_service.default_kb_service import DefaultKBService
            return DefaultKBService(kb_name)

    @staticmethod
    def get_service_by_name(kb_name: str
                            ) -> KBService:
        _, vs_type, embed_model = load_kb_from_db(kb_name)
        if vs_type is None and os.path.isdir(get_kb_path(kb_name)): # faiss knowledge base not in db
            vs_type = "faiss"
        return KBServiceFactory.get_service(kb_name, vs_type, embed_model)

    @staticmethod
    def get_default():
        return KBServiceFactory.get_service("default", SupportedVSType.DEFAULT)


def get_kb_details() -> List[Dict]:
    kbs_in_folder = list_kbs_from_folder()
    kbs_in_db = KBService.list_kbs()
    result = {}

    for kb in kbs_in_folder:
        result[kb] = {
            "kb_name": kb,
            "vs_type": "",
            "embed_model": "",
            "file_count": 0,
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }

    for kb in kbs_in_db:
        kb_detail = get_kb_detail(kb)
        if kb_detail:
            kb_detail["in_db"] = True
            if kb in result:
                result[kb].update(kb_detail)
            else:
                kb_detail["in_folder"] = False
                result[kb] = kb_detail

    data = []
    for i, v in enumerate(result.values()):
        v['No'] = i + 1
        data.append(v)
   
    return data


def get_kb_doc_details(kb_name: str) -> List[Dict]:
    kb = KBServiceFactory.get_service_by_name(kb_name)
    docs_in_folder = list_docs_from_folder(kb_name)
    docs_in_db = kb.list_docs()
    result = {}

    for doc in docs_in_folder:
        result[doc] = {
            "kb_name": kb_name,
            "file_name": doc,
            "file_ext": os.path.splitext(doc)[-1],
            "file_version": 0,
            "document_loader": "",
            "text_splitter": "",
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }
    for doc in docs_in_db:
        doc_detail = get_file_detail(kb_name, doc)
        if doc_detail:
            doc_detail["in_db"] = True
            if doc in result:
                result[doc].update(doc_detail)
            else:
                doc_detail["in_folder"] = False
                result[doc] = doc_detail

    data = []
    for i, v in enumerate(result.values()):
        v['No'] = i + 1
        data.append(v)
   
    return data

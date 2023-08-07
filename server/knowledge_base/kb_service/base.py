from abc import ABC, abstractmethod

import os
import sqlite3
from functools import lru_cache

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document

from configs.model_config import (DB_ROOT_PATH, kbs_config, VECTOR_SEARCH_TOP_K,
                                  embedding_model_dict, EMBEDDING_DEVICE, EMBEDDING_MODEL)
import datetime
from server.knowledge_base.utils import (get_kb_path, get_doc_path)
from server.knowledge_base.knowledge_file import KnowledgeFile
from typing import List


class SupportedVSType:
    FAISS = 'faiss'
    MILVUS = 'milvus'
    DEFAULT = 'default'


def init_db():
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists knowledge_base
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 kb_name TEXT, 
                 vs_type TEXT, 
                 embed_model TEXT,
                 file_count INTEGER,
                 create_time DATETIME) ''')
    c.execute('''CREATE TABLE if not exists knowledge_files
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     file_name TEXT, 
                     file_ext TEXT, 
                     kb_name TEXT,
                     document_loader_name TEXT,
                     text_splitter_name TEXT,
                     file_version INTEGER,
                     create_time DATETIME) ''')
    conn.commit()
    conn.close()


def list_kbs_from_db():
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute(f'''SELECT kb_name
                  FROM knowledge_base
                  WHERE file_count>0  ''')
    kbs = [i[0] for i in c.fetchall() if i]
    conn.commit()
    conn.close()
    return kbs


def add_kb_to_db(kb_name, vs_type, embed_model):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    # Insert a row of data
    c.execute(f"""INSERT INTO knowledge_base 
                  (kb_name, vs_type, embed_model, file_count, create_time)
                  VALUES 
                  ('{kb_name}','{vs_type}','{embed_model}',
                  0,'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')""")
    conn.commit()
    conn.close()
    return True


def kb_exists(kb_name):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute(f'''SELECT COUNT(*)
                  FROM knowledge_base
                  WHERE kb_name="{kb_name}"  ''')
    status = True if c.fetchone()[0] else False
    conn.commit()
    conn.close()
    return status


def load_kb_from_db(kb_name):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute(f'''SELECT kb_name, vs_type, embed_model
                  FROM knowledge_base
                  WHERE kb_name="{kb_name}"  ''')
    resp = c.fetchone()
    if resp:
        kb_name, vs_type, embed_model = resp
    else:
        kb_name, vs_type, embed_model = None, None, None
    conn.commit()
    conn.close()
    return kb_name, vs_type, embed_model


def delete_kb_from_db(kb_name):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute(f'''DELETE
                  FROM knowledge_base
                  WHERE kb_name="{kb_name}"  ''')
    c.execute(f"""DELETE 
                  FROM knowledge_files 
                  WHERE kb_name="{kb_name}"
                """)
    conn.commit()
    conn.close()
    return True


def list_docs_from_db(kb_name):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute(f'''SELECT file_name
                  FROM knowledge_files
                  WHERE kb_name="{kb_name}"  ''')
    kbs = [i[0] for i in c.fetchall() if i]
    conn.commit()
    conn.close()
    return kbs


def add_doc_to_db(kb_file: KnowledgeFile):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    # Insert a row of data
    c.execute(
        f"""SELECT 1 FROM knowledge_files WHERE file_name="{kb_file.filename}" AND kb_name="{kb_file.kb_name}" """)
    record_exist = c.fetchone()
    if record_exist is not None:
        c.execute(f"""UPDATE knowledge_files 
                      SET file_version = file_version + 1
                      WHERE file_name="{kb_file.filename}" AND kb_name="{kb_file.kb_name}"
                   """)
    else:
        c.execute(f"""INSERT INTO knowledge_files 
                      (file_name, file_ext, kb_name, document_loader_name, text_splitter_name, file_version, create_time)
                      VALUES 
                      ('{kb_file.filename}','{kb_file.ext}','{kb_file.kb_name}', '{kb_file.document_loader_name}', 
                      '{kb_file.text_splitter_name}',0,'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')""")
        c.execute(f"""UPDATE knowledge_base
                      SET file_count = file_count + 1 
                      WHERE kb_name="{kb_file.kb_name}"
                    """)
    conn.commit()
    conn.close()
    return True


def delete_file_from_db(kb_file: KnowledgeFile):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    # Insert a row of data
    c.execute(f"""DELETE 
                  FROM knowledge_files 
                  WHERE file_name="{kb_file.filename}"
                  AND kb_name="{kb_file.kb_name}"
                """)
    c.execute(f"""UPDATE knowledge_base
                  SET file_count = file_count - 1 
                  WHERE kb_name="{kb_file.kb_name}"
                """)
    conn.commit()
    conn.close()
    return True


def doc_exists(kb_file: KnowledgeFile):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute(f'''SELECT COUNT(*)
                  FROM knowledge_files
                  WHERE file_name="{kb_file.filename}"
                  AND kb_name="{kb_file.kb_name}"  ''')
    status = True if c.fetchone()[0] else False
    conn.commit()
    conn.close()
    return status


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

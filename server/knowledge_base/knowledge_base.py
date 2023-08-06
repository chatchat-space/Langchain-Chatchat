import os
import sqlite3
import datetime
import shutil
from langchain.vectorstores import FAISS
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from configs.model_config import (embedding_model_dict, EMBEDDING_MODEL, EMBEDDING_DEVICE,
                                  DB_ROOT_PATH, VECTOR_SEARCH_TOP_K, CACHED_VS_NUM)
from server.utils import torch_gc
from functools import lru_cache
from server.knowledge_base.knowledge_file import KnowledgeFile
from typing import List
import numpy as np
from server.knowledge_base.utils import (get_kb_path, get_doc_path, get_vs_path)

SUPPORTED_VS_TYPES = ["faiss", "milvus"]

_VECTOR_STORE_TICKS = {}

@lru_cache(1)
def load_embeddings(model: str, device: str):
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[model],
                                       model_kwargs={'device': device})
    return embeddings


@lru_cache(CACHED_VS_NUM)
def load_vector_store(
        knowledge_base_name: str,
        embedding_model: str,
        embedding_device: str,
        tick: int,  # tick will be changed by upload_doc etc. and make cache refreshed.
):
    print(f"loading vector store in '{knowledge_base_name}' with '{embedding_model}' embeddings.")
    embeddings = load_embeddings(embedding_model, embedding_device)
    vs_path = get_vs_path(knowledge_base_name)
    search_index = FAISS.load_local(vs_path, embeddings)
    return search_index


def refresh_vs_cache(kb_name: str):
    """
    make vector store cache refreshed when next loading
    """
    _VECTOR_STORE_TICKS[kb_name] = _VECTOR_STORE_TICKS.get(kb_name, 0) + 1


def list_kbs_from_db():
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists knowledge_base
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 kb_name TEXT, 
                 vs_type TEXT, 
                 embed_model TEXT,
                 file_count INTEGER,
                 create_time DATETIME) ''')
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
    # Create table
    c.execute('''CREATE TABLE if not exists knowledge_base
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 kb_name TEXT, 
                 vs_type TEXT, 
                 embed_model TEXT,
                 file_count INTEGER,
                 create_time DATETIME) ''')
    # Insert a row of data
    c.execute(f"""INSERT INTO knowledge_base 
                  (kb_name, vs_type, embed_model, file_count, create_time)
                  VALUES 
                  ('{kb_name}','{vs_type}','{embed_model}',
                  0,'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')""")
    conn.commit()
    conn.close()


def kb_exists(kb_name):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists knowledge_base
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 kb_name TEXT, 
                 vs_type TEXT, 
                 embed_model TEXT,
                 file_count INTEGER,
                 create_time DATETIME) ''')
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
    c.execute('''CREATE TABLE if not exists knowledge_base
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 kb_name TEXT, 
                 vs_type TEXT, 
                 embed_model TEXT,
                 file_count INTEGER,
                 create_time DATETIME) ''')
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
    # delete kb from table knowledge_base
    c.execute('''CREATE TABLE if not exists knowledge_base
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 kb_name TEXT, 
                 vs_type TEXT, 
                 embed_model TEXT,
                 file_count INTEGER,
                 create_time DATETIME) ''')
    c.execute(f'''DELETE
                  FROM knowledge_base
                  WHERE kb_name="{kb_name}"  ''')
    # delete files in kb from table knowledge_files
    c.execute('''CREATE TABLE if not exists knowledge_files
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     file_name TEXT, 
                     file_ext TEXT, 
                     kb_name TEXT,
                     document_loader_name TEXT,
                     text_splitter_name TEXT,
                     file_version INTEGER,
                     create_time DATETIME) ''')
    # Insert a row of data
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
    c.execute('''CREATE TABLE if not exists knowledge_files
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     file_name TEXT, 
                     file_ext TEXT, 
                     kb_name TEXT,
                     document_loader_name TEXT,
                     text_splitter_name TEXT,
                     file_version INTEGER,
                     create_time DATETIME) ''')
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
    # Create table
    c.execute('''CREATE TABLE if not exists knowledge_files
                 (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                 file_name TEXT, 
                 file_ext TEXT, 
                 kb_name TEXT,
                 document_loader_name TEXT,
                 text_splitter_name TEXT,
                 file_version INTEGER,
                 create_time DATETIME) ''')
    # Insert a row of data
    # TODO: 同名文件添加至知识库时，file_version增加
    c.execute(f"""SELECT 1 FROM knowledge_files WHERE file_name="{kb_file.filename}" AND kb_name="{kb_file.kb_name}" """)
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
    conn.commit()
    conn.close()


def delete_file_from_db(kb_file: KnowledgeFile):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    # delete files in kb from table knowledge_files
    c.execute('''CREATE TABLE if not exists knowledge_files
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     file_name TEXT, 
                     file_ext TEXT, 
                     kb_name TEXT,
                     document_loader_name TEXT,
                     text_splitter_name TEXT,
                     file_version INTEGER,
                     create_time DATETIME) ''')
    # Insert a row of data
    c.execute(f"""DELETE 
                  FROM knowledge_files 
                  WHERE file_name="{kb_file.filename}"
                  AND kb_name="{kb_file.kb_name}"
                """)
    conn.commit()
    conn.close()
    return True


def doc_exists(kb_file: KnowledgeFile):
    conn = sqlite3.connect(DB_ROOT_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists knowledge_files
                     (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                     file_name TEXT, 
                     file_ext TEXT, 
                     kb_name TEXT,
                     document_loader_name TEXT,
                     text_splitter_name TEXT,
                     file_version INTEGER,
                     create_time DATETIME) ''')
    c.execute(f'''SELECT COUNT(*)
                  FROM knowledge_files
                  WHERE file_name="{kb_file.filename}"
                  AND kb_name="{kb_file.kb_name}"  ''')
    status = True if c.fetchone()[0] else False
    conn.commit()
    conn.close()
    return status


def delete_doc_from_faiss(vector_store: FAISS, ids: List[str]):
    overlapping = set(ids).intersection(vector_store.index_to_docstore_id.values())
    if not overlapping:
        raise ValueError("ids do not exist in the current object")
    _reversed_index = {v: k for k, v in vector_store.index_to_docstore_id.items()}
    index_to_delete = [_reversed_index[i] for i in ids]
    vector_store.index.remove_ids(np.array(index_to_delete, dtype=np.int64))
    for _id in index_to_delete:
        del vector_store.index_to_docstore_id[_id]
    # Remove items from docstore.
    overlapping2 = set(ids).intersection(vector_store.docstore._dict)
    if not overlapping2:
        raise ValueError(f"Tried to delete ids that does not  exist: {ids}")
    for _id in ids:
        vector_store.docstore._dict.pop(_id)
    return vector_store


class KnowledgeBase:
    def __init__(self,
                 knowledge_base_name: str,
                 vector_store_type: str = "faiss",
                 embed_model: str = EMBEDDING_MODEL,
                 ):
        self.kb_name = knowledge_base_name
        if vector_store_type not in SUPPORTED_VS_TYPES:
            raise ValueError(f"暂未支持向量库类型 {vector_store_type}")
        self.vs_type = vector_store_type
        if embed_model not in embedding_model_dict.keys():
            raise ValueError(f"暂未支持embedding模型 {embed_model}")
        self.embed_model = embed_model
        self.kb_path = get_kb_path(self.kb_name)
        self.doc_path = get_doc_path(self.kb_name)
        if self.vs_type in ["faiss"]:
            self.vs_path = get_vs_path(self.kb_name)
        elif self.vs_type in ["milvus"]:
            pass

    def create(self):
        if not os.path.exists(self.doc_path):
            os.makedirs(self.doc_path)
        if self.vs_type in ["faiss"]:
            if not os.path.exists(self.vs_path):
                os.makedirs(self.vs_path)
            add_kb_to_db(self.kb_name, self.vs_type, self.embed_model)
        elif self.vs_type in ["milvus"]:
            # TODO: 创建milvus库
            pass
        return True

    def recreate_vs(self):
        if self.vs_type in ["faiss"]:
            shutil.rmtree(self.vs_path)
        self.create()

    def add_doc(self, kb_file: KnowledgeFile):
        docs = kb_file.file2text()
        embeddings = load_embeddings(self.embed_model, EMBEDDING_DEVICE)
        if self.vs_type in ["faiss"]:
            if os.path.exists(self.vs_path) and "index.faiss" in os.listdir(self.vs_path):
                vector_store = FAISS.load_local(self.vs_path, embeddings)
                vector_store.add_documents(docs)
                torch_gc()
            else:
                if not os.path.exists(self.vs_path):
                    os.makedirs(self.vs_path)
                vector_store = FAISS.from_documents(docs, embeddings)  # docs 为Document列表
                torch_gc()
            vector_store.save_local(self.vs_path)
            add_doc_to_db(kb_file)
            refresh_vs_cache(self.kb_name)
        elif self.vs_type in ["milvus"]:
            # TODO: 向milvus库中增加文件
            pass

    def delete_doc(self, kb_file: KnowledgeFile):
        if os.path.exists(kb_file.filepath):
            os.remove(kb_file.filepath)
        if self.vs_type in ["faiss"]:
            # TODO: 从FAISS向量库中删除文档
            embeddings = load_embeddings(self.embed_model, EMBEDDING_DEVICE)
            if os.path.exists(self.vs_path) and "index.faiss" in os.listdir(self.vs_path):
                vector_store = FAISS.load_local(self.vs_path, embeddings)
                ids = [k for k, v in vector_store.docstore._dict.items() if v.metadata["source"] == kb_file.filepath]
                if len(ids) == 0:
                    return None
                print(len(ids))
                vector_store = delete_doc_from_faiss(vector_store, ids)
                vector_store.save_local(self.vs_path)
                refresh_vs_cache(self.kb_name)
                delete_file_from_db(kb_file)
                return True

    def exist_doc(self, file_name: str):
        return doc_exists(KnowledgeFile(knowledge_base_name=self.kb_name,
                                        filename=file_name))

    def list_docs(self):
        return list_docs_from_db(self.kb_name)

    def search_docs(self,
                    query: str,
                    top_k: int = VECTOR_SEARCH_TOP_K,
                    embedding_device: str = EMBEDDING_DEVICE, ):
        search_index = load_vector_store(self.kb_name,
                                         self.embed_model,
                                         embedding_device,
                                         _VECTOR_STORE_TICKS.get(self.kb_name))
        docs = search_index.similarity_search(query, k=top_k)
        return docs

    @classmethod
    def exists(cls,
               knowledge_base_name: str):
        return kb_exists(knowledge_base_name)

    @classmethod
    def load(cls,
             knowledge_base_name: str):
        kb_name, vs_type, embed_model = load_kb_from_db(knowledge_base_name)
        return cls(kb_name, vs_type, embed_model)

    @classmethod
    def delete(cls,
               knowledge_base_name: str):
        kb = cls.load(knowledge_base_name)
        if kb.vs_type in ["faiss"]:
            shutil.rmtree(kb.kb_path)
        elif kb.vs_type in ["milvus"]:
            # TODO: 删除milvus库
            pass
        status = delete_kb_from_db(knowledge_base_name)
        return status

    @classmethod
    def list_kbs(cls):
        return list_kbs_from_db()


if __name__ == "__main__":
    # kb = KnowledgeBase("123", "faiss")
    # kb.create()
    kb = KnowledgeBase.load(knowledge_base_name="123")
    kb.delete_doc(KnowledgeFile(knowledge_base_name="123", filename="README.md"))
    print()

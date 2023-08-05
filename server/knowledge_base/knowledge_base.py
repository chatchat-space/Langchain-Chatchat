import os
import sqlite3
import datetime
import shutil
from langchain.vectorstores import FAISS
from server.knowledge_base.utils import (get_vs_path, get_kb_path, get_doc_path,
                                         refresh_vs_cache, load_embeddings)
from configs.model_config import (KB_ROOT_PATH, embedding_model_dict, EMBEDDING_MODEL,
                                  EMBEDDING_DEVICE)
from server.utils import torch_gc
from typing import List
from langchain.docstore.document import Document


SUPPORTED_VS_TYPES = ["faiss", "milvus"]
DB_ROOT = os.path.join(KB_ROOT_PATH, "info.db")


def list_kbs_from_db():
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''SELECT KB_NAME
                  FROM KNOWLEDGE_BASE
                  WHERE FILE_COUNT>0  ''')
    kbs = [i[0] for i in c.fetchall() if i]
    conn.commit()
    conn.close()
    return kbs


def add_kb_to_db(kb_name, vs_type, embed_model):
    conn = sqlite3.connect(DB_ROOT)
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
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''SELECT COUNT(*)
                  FROM knowledge_base
                  WHERE kb_name="{kb_name}"  ''')
    status = True if c.fetchone()[0] else False
    conn.commit()
    conn.close()
    return status


def load_kb_from_db(kb_name):
    conn = sqlite3.connect(DB_ROOT)
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
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''DELETE
                  FROM knowledge_base
                  WHERE kb_name="{kb_name}"  ''')
    conn.commit()
    conn.close()
    return True


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

    def add_file(self, docs: List[Document]):
        vs_path = get_vs_path(self.kb_name)
        embeddings = load_embeddings(embedding_model_dict[self.embed_model], EMBEDDING_DEVICE)
        if self.vs_type in ["faiss"]:
            if os.path.exists(vs_path) and "index.faiss" in os.listdir(vs_path):
                vector_store = FAISS.load_local(vs_path, embeddings)
                vector_store.add_documents(docs)
                torch_gc()
            else:
                if not os.path.exists(vs_path):
                    os.makedirs(vs_path)
                vector_store = FAISS.from_documents(docs, embeddings)  # docs 为Document列表
                torch_gc()
            vector_store.save_local(vs_path)
            refresh_vs_cache(self.kb_name)
        elif self.vs_type in ["milvus"]:
            # TODO: 向milvus库中增加文件
            pass

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
    print()

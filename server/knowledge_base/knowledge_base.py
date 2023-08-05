import os
import sqlite3
import datetime
import shutil
from langchain.vectorstores import FAISS
from server.knowledge_base.utils import (get_vs_path, get_kb_path, get_doc_path,
                                         refresh_vs_cache, load_embeddings)
from configs.model_config import (embedding_model_dict, EMBEDDING_MODEL,
                                  EMBEDDING_DEVICE, DB_ROOT_PATH)
from server.utils import torch_gc
from server.knowledge_base.knowledge_file import KnowledgeFile

SUPPORTED_VS_TYPES = ["faiss", "milvus"]


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
    c.execute(f"""INSERT INTO knowledge_files 
                  (file_name, file_ext, kb_name, document_loader_name, text_splitter_name, file_version, create_time)
                  VALUES 
                  ('{kb_file.filename}','{kb_file.ext}','{kb_file.kb_name}', '{kb_file.document_loader_name}', 
                  '{kb_file.text_splitter_name}',0,'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')""")
    conn.commit()
    conn.close()


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

    def add_doc(self, kb_file: KnowledgeFile):
        docs = kb_file.file2text()
        vs_path = get_vs_path(self.kb_name)
        embeddings = load_embeddings(self.embed_model, EMBEDDING_DEVICE)
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
            add_doc_to_db(kb_file)
            refresh_vs_cache(self.kb_name)
        elif self.vs_type in ["milvus"]:
            # TODO: 向milvus库中增加文件
            pass

    def list_docs(self):
        return list_docs_from_db(self.kb_name)

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

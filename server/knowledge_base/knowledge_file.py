import os.path
from server.knowledge_base.utils import (get_file_path, get_vs_path,
                                         refresh_vs_cache, load_embeddings)
from configs.model_config import (embedding_model_dict, EMBEDDING_MODEL, EMBEDDING_DEVICE)
from langchain.vectorstores import FAISS
from server.utils import torch_gc
from server.knowledge_base import KnowledgeBase


class KnowledgeFile:
    def __init__(
            self,
            filename: str,
            knowledge_base_name: str
    ):
        self.kb = KnowledgeBase.load(knowledge_base_name)
        self.knowledge_base_type = "faiss"
        self.filename = filename
        self.ext = os.path.splitext(filename)[-1]
        self.filepath = get_file_path(knowledge_base_name, filename)
        self.docs = None

    def file2text(self):
        if self.ext in []:
            from langchain.document_loaders import UnstructuredFileLoader
            loader = UnstructuredFileLoader(self.filepath)
        elif self.ext in []:
            pass

        from langchain.text_splitter import CharacterTextSplitter
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        return loader.load_and_split(text_splitter)

    def docs2vs(self):
        vs_path = get_vs_path(self.kb.kb_name)
        embeddings = load_embeddings(embedding_model_dict[EMBEDDING_MODEL], EMBEDDING_DEVICE)

        if os.path.exists(vs_path) and "index.faiss" in os.listdir(vs_path):
            vector_store = FAISS.load_local(vs_path, embeddings)
            vector_store.add_documents(self.docs)
            torch_gc()
        else:
            if not os.path.exists(vs_path):
                os.makedirs(vs_path)
            vector_store = FAISS.from_documents(self.docs, embeddings)  # docs 为Document列表
            torch_gc()
        vector_store.save_local(vs_path)
        refresh_vs_cache(self.kb.kb_name)
        return True
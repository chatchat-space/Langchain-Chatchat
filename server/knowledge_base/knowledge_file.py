import os.path
from server.knowledge_base.utils import (get_file_path)
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
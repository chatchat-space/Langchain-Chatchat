import os.path
from server.knowledge_base.utils import (get_file_path)
from server.knowledge_base import KnowledgeBase
import sys

LOADER_DICT = {"UnstructuredFileLoader": ['.eml', '.html', '.json', '.md', '.msg', '.rst',
                                          '.rtf', '.txt', '.xml',
                                          '.doc', '.docx', '.epub', '.odt', '.pdf',
                                          '.ppt', '.pptx', '.tsv'],  # '.pdf', '.xlsx', '.csv'
               "CSVLoader": [".csv"],
               }
SUPPORTED_EXTS = [ext for sublist in LOADER_DICT.values() for ext in sublist]

def get_LoaderClass(file_extension):
    for LoaderClass, extensions in LOADER_DICT.items():
        if file_extension in extensions:
            return LoaderClass


class KnowledgeFile:
    def __init__(
            self,
            filename: str,
            knowledge_base_name: str
    ):
        self.kb = KnowledgeBase.load(knowledge_base_name)
        self.filename = filename
        self.ext = os.path.splitext(filename)[-1]
        if self.ext not in SUPPORTED_EXTS:
            raise ValueError(f"暂未支持的文件格式 {self.ext}")
        self.filepath = get_file_path(knowledge_base_name, filename)
        self.docs = None
        self.loader_class_name = get_LoaderClass(self.ext)

    def file2text(self):
        LoaderClass = getattr(sys.modules['langchain.document_loaders'], self.loader_class_name)
        loader = LoaderClass(self.filepath)

        from langchain.text_splitter import CharacterTextSplitter
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        return loader.load_and_split(text_splitter)

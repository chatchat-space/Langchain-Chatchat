import os.path
from server.knowledge_base.utils import (get_file_path)
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
        self.kb_name = knowledge_base_name
        self.filename = filename
        self.ext = os.path.splitext(filename)[-1]
        if self.ext not in SUPPORTED_EXTS:
            raise ValueError(f"暂未支持的文件格式 {self.ext}")
        self.filepath = get_file_path(knowledge_base_name, filename)
        self.docs = None
        self.document_loader_name = get_LoaderClass(self.ext)

        # TODO: 增加依据文件格式匹配text_splitter
        self.text_splitter_name = "CharacterTextSplitter"

    def file2text(self):
        DocumentLoader = getattr(sys.modules['langchain.document_loaders'], self.document_loader_name)
        loader = DocumentLoader(self.filepath)

        # TODO: 增加依据文件格式匹配text_splitter
        TextSplitter = getattr(sys.modules['langchain.text_splitter'], self.text_splitter_name)
        text_splitter = TextSplitter(chunk_size=500, chunk_overlap=200)
        return loader.load_and_split(text_splitter)

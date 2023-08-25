import os
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceBgeEmbeddings
from configs.model_config import (
    embedding_model_dict,
    KB_ROOT_PATH,
    CHUNK_SIZE,
    OVERLAP_SIZE,
    ZH_TITLE_ENHANCE
)
from functools import lru_cache
import importlib
from text_splitter import zh_title_enhance


def validate_kb_name(knowledge_base_id: str) -> bool:
    # 检查是否包含预期外的字符或路径攻击关键字
    if "../" in knowledge_base_id:
        return False
    return True

def get_kb_path(knowledge_base_name: str):
    return os.path.join(KB_ROOT_PATH, knowledge_base_name)

def get_doc_path(knowledge_base_name: str):
    return os.path.join(get_kb_path(knowledge_base_name), "content")

def get_vs_path(knowledge_base_name: str):
    return os.path.join(get_kb_path(knowledge_base_name), "vector_store")

def get_file_path(knowledge_base_name: str, doc_name: str):
    return os.path.join(get_doc_path(knowledge_base_name), doc_name)

def list_kbs_from_folder():
    return [f for f in os.listdir(KB_ROOT_PATH)
            if os.path.isdir(os.path.join(KB_ROOT_PATH, f))]

def list_docs_from_folder(kb_name: str):
    doc_path = get_doc_path(kb_name)
    return [file for file in os.listdir(doc_path)
            if os.path.isfile(os.path.join(doc_path, file))]

@lru_cache(1)
def load_embeddings(model: str, device: str):
    if model == "text-embedding-ada-002":  # openai text-embedding-ada-002
        embeddings = OpenAIEmbeddings(openai_api_key=embedding_model_dict[model], chunk_size=CHUNK_SIZE)
    elif 'bge-' in model:
        embeddings = HuggingFaceBgeEmbeddings(model_name=embedding_model_dict[model],
                                              model_kwargs={'device': device},
                                              query_instruction="为这个句子生成表示以用于检索相关文章：")
        if model == "bge-large-zh-noinstruct":  # bge large -noinstruct embedding
            embeddings.query_instruction = ""
    else:
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[model], model_kwargs={'device': device})
    return embeddings



LOADER_DICT = {"UnstructuredFileLoader": ['.eml', '.html', '.json', '.md', '.msg', '.rst',
                                          '.rtf', '.txt', '.xml',
                                          '.doc', '.docx', '.epub', '.odt', '.pdf',
                                          '.ppt', '.pptx', '.tsv'],  # '.pdf', '.xlsx', '.csv'
               "CSVLoader": [".csv"],
               "PyPDFLoader": [".pdf"],
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
        self.ext = os.path.splitext(filename)[-1].lower()
        if self.ext not in SUPPORTED_EXTS:
            raise ValueError(f"暂未支持的文件格式 {self.ext}")
        self.filepath = get_file_path(knowledge_base_name, filename)
        self.docs = None
        self.document_loader_name = get_LoaderClass(self.ext)

        # TODO: 增加依据文件格式匹配text_splitter
        self.text_splitter_name = None

    def file2text(self, using_zh_title_enhance=ZH_TITLE_ENHANCE):
        print(self.document_loader_name)
        try:
            document_loaders_module = importlib.import_module('langchain.document_loaders')
            DocumentLoader = getattr(document_loaders_module, self.document_loader_name)
        except Exception as e:
            print(e)
            document_loaders_module = importlib.import_module('langchain.document_loaders')
            DocumentLoader = getattr(document_loaders_module, "UnstructuredFileLoader")
        if self.document_loader_name == "UnstructuredFileLoader":
            loader = DocumentLoader(self.filepath, autodetect_encoding=True)
        else:
            loader = DocumentLoader(self.filepath)

        try:
            if self.text_splitter_name is None:
                text_splitter_module = importlib.import_module('langchain.text_splitter')
                TextSplitter = getattr(text_splitter_module, "SpacyTextSplitter")
                text_splitter = TextSplitter(
                    pipeline="zh_core_web_sm",
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=OVERLAP_SIZE,
                )
                self.text_splitter_name = "SpacyTextSplitter"
            else:
                text_splitter_module = importlib.import_module('langchain.text_splitter')
                TextSplitter = getattr(text_splitter_module, self.text_splitter_name)
                text_splitter = TextSplitter(
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=OVERLAP_SIZE)
        except Exception as e:
            print(e)
            text_splitter_module = importlib.import_module('langchain.text_splitter')
            TextSplitter = getattr(text_splitter_module, "RecursiveCharacterTextSplitter")
            text_splitter = TextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=OVERLAP_SIZE,
            )

        docs = loader.load_and_split(text_splitter)
        print(docs[0])
        if using_zh_title_enhance:
            docs = zh_title_enhance(docs)
        return docs

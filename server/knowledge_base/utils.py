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
import langchain.document_loaders
from langchain.docstore.document import Document
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Union, Callable, Dict, Optional, Tuple, Generator


# make HuggingFaceEmbeddings hashable
def _embeddings_hash(self):
    if isinstance(self, HuggingFaceEmbeddings):
        return hash(self.model_name)
    elif isinstance(self, HuggingFaceBgeEmbeddings):
        return hash(self.model_name)
    elif isinstance(self, OpenAIEmbeddings):
        return hash(self.model)

HuggingFaceEmbeddings.__hash__ = _embeddings_hash
OpenAIEmbeddings.__hash__ = _embeddings_hash
HuggingFaceBgeEmbeddings.__hash__ = _embeddings_hash


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


def list_files_from_folder(kb_name: str):
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


LOADER_DICT = {"UnstructuredHTMLLoader": ['.html'],
               "UnstructuredMarkdownLoader": ['.md'],
               "CustomJSONLoader": [".json"],
               "CSVLoader": [".csv"],
               "RapidOCRPDFLoader": [".pdf"],
               "RapidOCRLoader": ['.png', '.jpg', '.jpeg', '.bmp'],
               "UnstructuredFileLoader": ['.eml', '.msg', '.rst',
                                          '.rtf', '.txt', '.xml',
                                          '.doc', '.docx', '.epub', '.odt',
                                          '.ppt', '.pptx', '.tsv'],  # '.xlsx'
               }
SUPPORTED_EXTS = [ext for sublist in LOADER_DICT.values() for ext in sublist]


class CustomJSONLoader(langchain.document_loaders.JSONLoader):
    '''
    langchain的JSONLoader需要jq，在win上使用不便，进行替代。
    '''

    def __init__(
            self,
            file_path: Union[str, Path],
            content_key: Optional[str] = None,
            metadata_func: Optional[Callable[[Dict, Dict], Dict]] = None,
            text_content: bool = True,
            json_lines: bool = False,
    ):
        """Initialize the JSONLoader.

        Args:
            file_path (Union[str, Path]): The path to the JSON or JSON Lines file.
            content_key (str): The key to use to extract the content from the JSON if
                results to a list of objects (dict).
            metadata_func (Callable[Dict, Dict]): A function that takes in the JSON
                object extracted by the jq_schema and the default metadata and returns
                a dict of the updated metadata.
            text_content (bool): Boolean flag to indicate whether the content is in
                string format, default to True.
            json_lines (bool): Boolean flag to indicate whether the input is in
                JSON Lines format.
        """
        self.file_path = Path(file_path).resolve()
        self._content_key = content_key
        self._metadata_func = metadata_func
        self._text_content = text_content
        self._json_lines = json_lines

    # TODO: langchain's JSONLoader.load has a encoding bug, raise gbk encoding error on windows.
    # This is a workaround for langchain==0.0.266. I have make a pr(#9785) to langchain, it should be deleted after langchain upgraded.
    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""
        docs: List[Document] = []
        if self._json_lines:
            with self.file_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._parse(line, docs)
        else:
            self._parse(self.file_path.read_text(encoding="utf-8"), docs)
        return docs

    def _parse(self, content: str, docs: List[Document]) -> None:
        """Convert given content to documents."""
        data = json.loads(content)

        # Perform some validation
        # This is not a perfect validation, but it should catch most cases
        # and prevent the user from getting a cryptic error later on.
        if self._content_key is not None:
            self._validate_content_key(data)

        for i, sample in enumerate(data, len(docs) + 1):
            metadata = dict(
                source=str(self.file_path),
                seq_num=i,
            )
            text = self._get_text(sample=sample, metadata=metadata)
            docs.append(Document(page_content=text, metadata=metadata))


langchain.document_loaders.CustomJSONLoader = CustomJSONLoader


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

    def file2text(self, using_zh_title_enhance=ZH_TITLE_ENHANCE, refresh: bool = False):
        if self.docs is not None and not refresh:
            return self.docs

        print(f"{self.document_loader_name} used for {self.filepath}")
        try:
            if self.document_loader_name in ["RapidOCRPDFLoader", "RapidOCRLoader"]:
                document_loaders_module = importlib.import_module('document_loaders')
            else:
                document_loaders_module = importlib.import_module('langchain.document_loaders')
            DocumentLoader = getattr(document_loaders_module, self.document_loader_name)
        except Exception as e:
            print(e)
            document_loaders_module = importlib.import_module('langchain.document_loaders')
            DocumentLoader = getattr(document_loaders_module, "UnstructuredFileLoader")
        if self.document_loader_name == "UnstructuredFileLoader":
            loader = DocumentLoader(self.filepath, autodetect_encoding=True)
        elif self.document_loader_name == "CSVLoader":
            loader = DocumentLoader(self.filepath, encoding="utf-8")
        elif self.document_loader_name == "JSONLoader":
            loader = DocumentLoader(self.filepath, jq_schema=".", text_content=False)
        elif self.document_loader_name == "CustomJSONLoader":
            loader = DocumentLoader(self.filepath, text_content=False)
        elif self.document_loader_name == "UnstructuredMarkdownLoader":
            loader = DocumentLoader(self.filepath, mode="elements")
        elif self.document_loader_name == "UnstructuredHTMLLoader":
            loader = DocumentLoader(self.filepath, mode="elements")
        else:
            loader = DocumentLoader(self.filepath)

        if self.ext in ".csv":
            docs = loader.load()
        else:
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
        self.docs = docs
        return docs

    def get_mtime(self):
        return os.path.getmtime(self.filepath)

    def get_size(self):
        return os.path.getsize(self.filepath)


def run_in_thread_pool(
    func: Callable,
    params: List[Dict] = [],
    pool: ThreadPoolExecutor = None,
) -> Generator:
    '''
    在线程池中批量运行任务，并将运行结果以生成器的形式返回。
    请确保任务中的所有操作是线程安全的，任务函数请全部使用关键字参数。
    '''
    tasks = []
    if pool is None:
        pool = ThreadPoolExecutor()
    
    for kwargs in params:
        thread = pool.submit(func, **kwargs)
        tasks.append(thread)
    
    for obj in as_completed(tasks):
        yield obj.result()


def files2docs_in_thread(
    files: List[Union[KnowledgeFile, Tuple[str, str], Dict]],
    pool: ThreadPoolExecutor = None,
) -> Generator:
    '''
    利用多线程批量将文件转化成langchain Document.
    生成器返回值为{(kb_name, file_name): docs}
    '''
    def task(*, file: KnowledgeFile, **kwargs) -> Dict[Tuple[str, str], List[Document]]:
        try:
            return True, (file.kb_name, file.filename, file.file2text(**kwargs))
        except Exception as e:
            return False, e

    kwargs_list = []
    for i, file in enumerate(files):
        kwargs = {}
        if isinstance(file, tuple) and len(file) >= 2:
            files[i] = KnowledgeFile(filename=file[0], knowledge_base_name=file[1])
        elif isinstance(file, dict):
            filename = file.pop("filename")
            kb_name = file.pop("kb_name")
            files[i] = KnowledgeFile(filename=filename, knowledge_base_name=kb_name)
            kwargs = file
        kwargs["file"] = file
        kwargs_list.append(kwargs)
    
    for result in run_in_thread_pool(func=task, params=kwargs_list, pool=pool):
        yield result

import os
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceBgeEmbeddings
from configs.model_config import (
    embedding_model_dict,
    EMBEDDING_MODEL,
    KB_ROOT_PATH,
    CHUNK_SIZE,
    OVERLAP_SIZE,
    ZH_TITLE_ENHANCE,
    logger, log_verbose,
)
import importlib
from text_splitter import zh_title_enhance
import langchain.document_loaders
from langchain.docstore.document import Document
from langchain.text_splitter import TextSplitter
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor
from server.utils import run_in_thread_pool, embedding_device
import io
from typing import List, Union, Callable, Dict, Optional, Tuple, Generator


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


def load_embeddings(model: str = EMBEDDING_MODEL, device: str = embedding_device()):
    '''
    从缓存中加载embeddings，可以避免多线程时竞争加载。
    '''
    from server.knowledge_base.kb_cache.base import embeddings_pool
    return embeddings_pool.load_embeddings(model=model, device=device)


LOADER_DICT = {"UnstructuredHTMLLoader": ['.html'],
               "UnstructuredMarkdownLoader": ['.md'],
               "CustomJSONLoader": [".json"],
               "CSVLoader": [".csv"],
               "RapidOCRPDFLoader": [".pdf"],
               "RapidOCRLoader": ['.png', '.jpg', '.jpeg', '.bmp'],
               "UnstructuredFileLoader": ['.eml', '.msg', '.rst',
                                          '.rtf', '.txt', '.xml',
                                          '.docx', '.epub', '.odt',
                                          '.ppt', '.pptx', '.tsv'],
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


# 把一些向量化共用逻辑从KnowledgeFile抽取出来，等langchain支持内存文件的时候，可以将非磁盘文件向量化
def get_loader(loader_name: str, file_path_or_content: Union[str, bytes, io.StringIO, io.BytesIO]):
    '''
    根据loader_name和文件路径或内容返回文档加载器。
    '''
    try:
        if loader_name in ["RapidOCRPDFLoader", "RapidOCRLoader"]:
            document_loaders_module = importlib.import_module('document_loaders')
        else:
            document_loaders_module = importlib.import_module('langchain.document_loaders')
        DocumentLoader = getattr(document_loaders_module, loader_name)
    except Exception as e:
        msg = f"为文件{file_path_or_content}查找加载器{loader_name}时出错：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        document_loaders_module = importlib.import_module('langchain.document_loaders')
        DocumentLoader = getattr(document_loaders_module, "UnstructuredFileLoader")

    if loader_name == "UnstructuredFileLoader":
        loader = DocumentLoader(file_path_or_content, autodetect_encoding=True)
    elif loader_name == "CSVLoader":
        loader = DocumentLoader(file_path_or_content, encoding="utf-8")
    elif loader_name == "JSONLoader":
        loader = DocumentLoader(file_path_or_content, jq_schema=".", text_content=False)
    elif loader_name == "CustomJSONLoader":
        loader = DocumentLoader(file_path_or_content, text_content=False)
    elif loader_name == "UnstructuredMarkdownLoader":
        loader = DocumentLoader(file_path_or_content, mode="elements")
    elif loader_name == "UnstructuredHTMLLoader":
        loader = DocumentLoader(file_path_or_content, mode="elements")
    else:
        loader = DocumentLoader(file_path_or_content)
    return loader


def make_text_splitter(
    splitter_name: str = "SpacyTextSplitter",
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = OVERLAP_SIZE,
):
    '''
    根据参数获取特定的分词器
    '''
    splitter_name = splitter_name or "SpacyTextSplitter"
    text_splitter_module = importlib.import_module('langchain.text_splitter')
    try:
        TextSplitter = getattr(text_splitter_module, splitter_name)
        text_splitter = TextSplitter(
            pipeline="zh_core_web_sm",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    except Exception as e:
        msg = f"查找分词器 {splitter_name} 时出错：{e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        TextSplitter = getattr(text_splitter_module, "RecursiveCharacterTextSplitter")
        text_splitter = TextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    return text_splitter

class KnowledgeFile:
    def __init__(
            self,
            filename: str,
            knowledge_base_name: str
    ):
        '''
        对应知识库目录中的文件，必须是磁盘上存在的才能进行向量化等操作。
        '''
        self.kb_name = knowledge_base_name
        self.filename = filename
        self.ext = os.path.splitext(filename)[-1].lower()
        if self.ext not in SUPPORTED_EXTS:
            raise ValueError(f"暂未支持的文件格式 {self.ext}")
        self.filepath = get_file_path(knowledge_base_name, filename)
        self.docs = None
        self.splited_docs = None
        self.document_loader_name = get_LoaderClass(self.ext)

        # TODO: 增加依据文件格式匹配text_splitter
        self.text_splitter_name = None

    def file2docs(self, refresh: bool=False):
        if self.docs is None or refresh:
            logger.info(f"{self.document_loader_name} used for {self.filepath}")
            loader = get_loader(self.document_loader_name, self.filepath)
            self.docs = loader.load()
        return self.docs

    def docs2texts(
        self,
        docs: List[Document] = None,
        using_zh_title_enhance=ZH_TITLE_ENHANCE,
        refresh: bool = False,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
        text_splitter: TextSplitter = None,
    ):
        docs = docs or self.file2docs(refresh=refresh)
        if not docs:
            return []
        if self.ext not in [".csv"]:
            if text_splitter is None:
                text_splitter = make_text_splitter(splitter_name=self.text_splitter_name, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            docs = text_splitter.split_documents(docs)

        print(f"文档切分示例：{docs[0]}")
        if using_zh_title_enhance:
            docs = zh_title_enhance(docs)
        self.splited_docs = docs
        return self.splited_docs

    def file2text(
        self,
        using_zh_title_enhance=ZH_TITLE_ENHANCE,
        refresh: bool = False,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
        text_splitter: TextSplitter = None,
    ):
        if self.splited_docs is None or refresh:
            docs = self.file2docs()
            self.splited_docs = self.docs2texts(docs=docs,
                                                using_zh_title_enhance=using_zh_title_enhance,
                                                refresh=refresh,
                                                chunk_size=chunk_size,
                                                chunk_overlap=chunk_overlap,
                                                text_splitter=text_splitter)
        return self.splited_docs

    def file_exist(self):
        return os.path.isfile(self.filepath)

    def get_mtime(self):
        return os.path.getmtime(self.filepath)

    def get_size(self):
        return os.path.getsize(self.filepath)


def files2docs_in_thread(
        files: List[Union[KnowledgeFile, Tuple[str, str], Dict]],
        pool: ThreadPoolExecutor = None,
) -> Generator:
    '''
    利用多线程批量将磁盘文件转化成langchain Document.
    如果传入参数是Tuple，形式为(filename, kb_name)
    生成器返回值为 status, (kb_name, file_name, docs | error)
    '''
    def file2docs(*, file: KnowledgeFile, **kwargs) -> Tuple[bool, Tuple[str, str, List[Document]]]:
        try:
            return True, (file.kb_name, file.filename, file.file2text(**kwargs))
        except Exception as e:
            msg = f"从文件 {file.kb_name}/{file.filename} 加载文档时出错：{e}"
            logger.error(f'{e.__class__.__name__}: {msg}',
                         exc_info=e if log_verbose else None)
            return False, (file.kb_name, file.filename, msg)

    kwargs_list = []
    for i, file in enumerate(files):
        kwargs = {}
        if isinstance(file, tuple) and len(file) >= 2:
            file = KnowledgeFile(filename=file[0], knowledge_base_name=file[1])
        elif isinstance(file, dict):
            filename = file.pop("filename")
            kb_name = file.pop("kb_name")
            kwargs = file
            file = KnowledgeFile(filename=filename, knowledge_base_name=kb_name)
        kwargs["file"] = file
        kwargs_list.append(kwargs)

    for result in run_in_thread_pool(func=file2docs, params=kwargs_list, pool=pool):
        yield result


if __name__ == "__main__":
    from pprint import pprint

    kb_file = KnowledgeFile(filename="test.txt", knowledge_base_name="samples")
    # kb_file.text_splitter_name = "RecursiveCharacterTextSplitter"
    docs = kb_file.file2docs()
    pprint(docs[-1])

    docs = kb_file.file2text()
    pprint(docs[-1])

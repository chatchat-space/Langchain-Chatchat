import os

from transformers import AutoTokenizer

from configs.model_config import (
    EMBEDDING_MODEL,
    KB_ROOT_PATH,
    CHUNK_SIZE,
    OVERLAP_SIZE,
    ZH_TITLE_ENHANCE,
    logger, 
    log_verbose, 
    text_splitter_dict, 
    llm_model_dict, 
    LLM_MODEL, 
    TEXT_SPLITTER
)
import importlib
from text_splitter import zh_title_enhance as func_zh_title_enhance
import langchain.document_loaders
from langchain.docstore.document import Document
from langchain.text_splitter import TextSplitter
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor
from server.utils import run_in_thread_pool, embedding_device
import io
from typing import List, Union, Callable, Dict, Optional, Tuple, Generator
import chardet


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
    langchain的JSONLoader需要jq，在win上使用不便，进行替代。针对langchain==0.0.286
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

    def _parse(self, content: str, docs: List[Document]) -> None:
        """Convert given content to documents."""
        data = json.loads(content)

        # Perform some validation
        # This is not a perfect validation, but it should catch most cases
        # and prevent the user from getting a cryptic error later on.
        if self._content_key is not None:
            self._validate_content_key(data)
        if self._metadata_func is not None:
            self._validate_metadata_func(data)

        for i, sample in enumerate(data, len(docs) + 1):
            text = self._get_text(sample=sample)
            metadata = self._get_metadata(
                sample=sample, source=str(self.file_path), seq_num=i
            )
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
        # 自动识别文件编码类型，避免langchain loader 加载文件报编码错误
        with open(file_path_or_content, 'rb') as struct_file:
            encode_detect = chardet.detect(struct_file.read())
        if encode_detect:
            loader = DocumentLoader(file_path_or_content, encoding=encode_detect["encoding"])
        else:
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
    splitter_name: str = TEXT_SPLITTER,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = OVERLAP_SIZE,
):
    """
    根据参数获取特定的分词器
    """
    splitter_name = splitter_name or "SpacyTextSplitter"
    try:
        if splitter_name == "MarkdownHeaderTextSplitter":  # MarkdownHeaderTextSplitter特殊判定
            headers_to_split_on = text_splitter_dict[splitter_name]['headers_to_split_on']
            text_splitter = langchain.text_splitter.MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on)
        else:

            try:  ## 优先使用用户自定义的text_splitter
                text_splitter_module = importlib.import_module('text_splitter')
                TextSplitter = getattr(text_splitter_module, splitter_name)
            except:  ## 否则使用langchain的text_splitter
                text_splitter_module = importlib.import_module('langchain.text_splitter')
                TextSplitter = getattr(text_splitter_module, splitter_name)

            if text_splitter_dict[splitter_name]["source"] == "tiktoken":  ## 从tiktoken加载
                try:
                    text_splitter = TextSplitter.from_tiktoken_encoder(
                        encoding_name=text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                        pipeline="zh_core_web_sm",
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                except:
                    text_splitter = TextSplitter.from_tiktoken_encoder(
                        encoding_name=text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
            elif text_splitter_dict[splitter_name]["source"] == "huggingface":  ## 从huggingface加载
                if text_splitter_dict[splitter_name]["tokenizer_name_or_path"] == "":
                    text_splitter_dict[splitter_name]["tokenizer_name_or_path"] = \
                        llm_model_dict[LLM_MODEL]["local_model_path"]

                if text_splitter_dict[splitter_name]["tokenizer_name_or_path"] == "gpt2":
                    from transformers import GPT2TokenizerFast
                    from langchain.text_splitter import CharacterTextSplitter
                    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
                else:  ## 字符长度加载
                    tokenizer = AutoTokenizer.from_pretrained(
                        text_splitter_dict[splitter_name]["tokenizer_name_or_path"],
                        trust_remote_code=True)
                text_splitter = TextSplitter.from_huggingface_tokenizer(
                    tokenizer=tokenizer,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            else:
                try:
                    text_splitter = TextSplitter(
                        pipeline="zh_core_web_sm",
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                except:
                    text_splitter = TextSplitter(
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
    except Exception as e:
        print(e)
        text_splitter_module = importlib.import_module('langchain.text_splitter')
        TextSplitter = getattr(text_splitter_module, "RecursiveCharacterTextSplitter")
        text_splitter = TextSplitter(chunk_size=250, chunk_overlap=50)
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
        self.text_splitter_name = TEXT_SPLITTER

    def file2docs(self, refresh: bool=False):
        if self.docs is None or refresh:
            logger.info(f"{self.document_loader_name} used for {self.filepath}")
            loader = get_loader(self.document_loader_name, self.filepath)
            self.docs = loader.load()
        return self.docs

    def docs2texts(
        self,
        docs: List[Document] = None,
        zh_title_enhance: bool = ZH_TITLE_ENHANCE,
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
            if self.text_splitter_name == "MarkdownHeaderTextSplitter":
                docs = text_splitter.split_text(docs[0].page_content)
                for doc in docs:
                    # 如果文档有元数据
                    if doc.metadata:
                        doc.metadata["source"] = os.path.basename(self.filepath)
            else:
                docs = text_splitter.split_documents(docs)

        print(f"文档切分示例：{docs[0]}")
        if zh_title_enhance:
            docs = func_zh_title_enhance(docs)
        self.splited_docs = docs
        return self.splited_docs

    def file2text(
        self,
        zh_title_enhance: bool = ZH_TITLE_ENHANCE,
        refresh: bool = False,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
        text_splitter: TextSplitter = None,
    ):
        if self.splited_docs is None or refresh:
            docs = self.file2docs()
            self.splited_docs = self.docs2texts(docs=docs,
                                                zh_title_enhance=zh_title_enhance,
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
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = OVERLAP_SIZE,
        zh_title_enhance: bool = ZH_TITLE_ENHANCE,
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
        kwargs["chunk_size"] = chunk_size
        kwargs["chunk_overlap"] = chunk_overlap
        kwargs["zh_title_enhance"] = zh_title_enhance
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
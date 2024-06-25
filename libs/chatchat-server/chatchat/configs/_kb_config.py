import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

sys.path.append(str(Path(__file__).parent))
import _core_config as core_config
from _basic_config import config_basic_workspace


class ConfigKb(core_config.Config):
    DEFAULT_KNOWLEDGE_BASE: Optional[str] = None
    """默认使用的知识库"""
    DEFAULT_VS_TYPE: Optional[str] = None
    """默认向量库/全文检索引擎类型。可选：faiss, milvus(离线) & zilliz(在线), pgvector,全文检索引擎es"""
    CACHED_VS_NUM: Optional[int] = None
    """缓存向量库数量（针对FAISS）"""
    CACHED_MEMO_VS_NUM: Optional[int] = None
    """缓存临时向量库数量（针对FAISS），用于文件对话"""
    CHUNK_SIZE: Optional[int] = None
    """知识库中单段文本长度(不适用MarkdownHeaderTextSplitter)"""
    OVERLAP_SIZE: Optional[int] = None
    """知识库中相邻文本重合长度(不适用MarkdownHeaderTextSplitter)"""
    VECTOR_SEARCH_TOP_K: Optional[int] = None
    """知识库匹配向量数量"""
    SCORE_THRESHOLD: Optional[float] = None
    """知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右"""
    DEFAULT_SEARCH_ENGINE: Optional[str] = None
    """默认搜索引擎。可选：bing, duckduckgo, metaphor"""
    SEARCH_ENGINE_TOP_K: Optional[int] = None
    """搜索引擎匹配结题数量"""
    ZH_TITLE_ENHANCE: Optional[bool] = None
    """是否开启中文标题加强，以及标题增强的相关配置"""
    PDF_OCR_THRESHOLD: Optional[Tuple[float, float]] = None
    """
    PDF OCR 控制：只对宽高超过页面一定比例（图片宽/页面宽，图片高/页面高）的图片进行 OCR。
    这样可以避免 PDF 中一些小图片的干扰，提高非扫描版 PDF 处理速度
    """
    KB_INFO: Optional[Dict[str, str]] = None
    """每个知识库的初始化介绍，用于在初始化知识库时显示和Agent调用，没写则没有介绍，不会被Agent调用。"""
    KB_ROOT_PATH: Optional[str] = None
    """知识库默认存储路径"""
    DB_ROOT_PATH: Optional[str] = None
    """数据库默认存储路径。如果使用sqlite，可以直接修改DB_ROOT_PATH；如果使用其它数据库，请直接修改SQLALCHEMY_DATABASE_URI。"""
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    """数据库连接URI"""
    kbs_config: Optional[Dict[str, Dict[str, Any]]] = None
    """可选向量库类型及对应配置"""
    text_splitter_dict: Optional[Dict[str, Dict[str, Any]]] = None
    """TextSplitter配置项，如果你不明白其中的含义，就不要修改。"""
    TEXT_SPLITTER_NAME: Optional[str] = None
    """TEXT_SPLITTER 名称"""
    EMBEDDING_KEYWORD_FILE: Optional[str] = None
    """Embedding模型定制词语的词表文件"""

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return self.to_json()


@dataclass
class ConfigKbFactory(core_config.ConfigFactory[ConfigKb]):
    """ConfigKb 配置工厂类"""

    def __init__(self):
        # 默认使用的知识库
        self.DEFAULT_KNOWLEDGE_BASE = "samples"

        # 默认向量库/全文检索引擎类型。可选：faiss, milvus(离线) & zilliz(在线), pgvector,全文检索引擎es,relyt
        self.DEFAULT_VS_TYPE = "faiss"

        # 缓存向量库数量（针对FAISS）
        self.CACHED_VS_NUM = 1

        # 缓存临时向量库数量（针对FAISS），用于文件对话
        self.CACHED_MEMO_VS_NUM = 10

        # 知识库中单段文本长度(不适用MarkdownHeaderTextSplitter)
        self.CHUNK_SIZE = 250

        # 知识库中相邻文本重合长度(不适用MarkdownHeaderTextSplitter)
        self.OVERLAP_SIZE = 50

        # 知识库匹配向量数量
        self.VECTOR_SEARCH_TOP_K = 3

        # 知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右
        self.SCORE_THRESHOLD = 1

        # 默认搜索引擎。可选：bing, duckduckgo, metaphor
        self.DEFAULT_SEARCH_ENGINE = "duckduckgo"

        # 搜索引擎匹配结题数量
        self.SEARCH_ENGINE_TOP_K = 3

        # 是否开启中文标题加强，以及标题增强的相关配置
        # 通过增加标题判断，判断哪些文本为标题，并在metadata中进行标记；
        # 然后将文本与往上一级的标题进行拼合，实现文本信息的增强。
        self.ZH_TITLE_ENHANCE = False

        # PDF OCR 控制：只对宽高超过页面一定比例（图片宽/页面宽，图片高/页面高）的图片进行 OCR。
        # 这样可以避免 PDF 中一些小图片的干扰，提高非扫描版 PDF 处理速度
        self.PDF_OCR_THRESHOLD = (0.6, 0.6)

        # 每个知识库的初始化介绍，用于在初始化知识库时显示和Agent调用，没写则没有介绍，不会被Agent调用。
        self.KB_INFO = {
            "samples": "关于本项目issue的解答",
        }

        # 通常情况下不需要更改以下内容

        # 知识库默认存储路径
        self.KB_ROOT_PATH = os.path.join(
            config_basic_workspace.get_config().DATA_PATH, "knowledge_base"
        )
        if not os.path.exists(self.KB_ROOT_PATH):
            os.mkdir(self.KB_ROOT_PATH)

        # 数据库默认存储路径。
        # 如果使用sqlite，可以直接修改DB_ROOT_PATH；如果使用其它数据库，请直接修改SQLALCHEMY_DATABASE_URI。
        self.DB_ROOT_PATH = os.path.join(self.KB_ROOT_PATH, "info.db")
        self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{self.DB_ROOT_PATH}"

        # 可选向量库类型及对应配置
        self.kbs_config = {
            "faiss": {},
            "milvus": {
                "host": "127.0.0.1",
                "port": "19530",
                "user": "",
                "password": "",
                "secure": False,
            },
            "zilliz": {
                "host": "in01-a7ce524e41e3935.ali-cn-hangzhou.vectordb.zilliz.com.cn",
                "port": "19530",
                "user": "",
                "password": "",
                "secure": True,
            },
            "pg": {
                "connection_uri": "postgresql://postgres:postgres@127.0.0.1:5432/langchain_chatchat",
            },
            "relyt": {
                "connection_uri": "postgresql+psycopg2://postgres:postgres@127.0.0.1:7000/langchain_chatchat",
            },
            "es": {
                "host": "127.0.0.1",
                "port": "9200",
                "index_name": "test_index",
                "user": "",
                "password": "",
            },
            "milvus_kwargs": {
                "search_params": {"metric_type": "L2"},  # 在此处增加search_params
                "index_params": {
                    "metric_type": "L2",
                    "index_type": "HNSW",
                },  # 在此处增加index_params
            },
            "chromadb": {},
        }

        # TextSplitter配置项，如果你不明白其中的含义，就不要修改。
        self.text_splitter_dict = {
            "ChineseRecursiveTextSplitter": {
                "source": "",  # 选择tiktoken则使用openai的方法 "huggingface"
                "tokenizer_name_or_path": "",
            },
            "SpacyTextSplitter": {
                "source": "huggingface",
                "tokenizer_name_or_path": "gpt2",
            },
            "RecursiveCharacterTextSplitter": {
                "source": "tiktoken",
                "tokenizer_name_or_path": "cl100k_base",
            },
            "MarkdownHeaderTextSplitter": {
                "headers_to_split_on": [
                    ("#", "head1"),
                    ("##", "head2"),
                    ("###", "head3"),
                    ("####", "head4"),
                ]
            },
        }

        # TEXT_SPLITTER 名称
        self.TEXT_SPLITTER_NAME = "ChineseRecursiveTextSplitter"

        # Embedding模型定制词语的词表文件
        self.EMBEDDING_KEYWORD_FILE = "embedding_keywords.txt"

    def get_config(self) -> ConfigKb:
        config = ConfigKb()
        for key, value in self.__dict__.items():
            setattr(config, key, value)

        return config


class ConfigKbWorkSpace(core_config.ConfigWorkSpace[ConfigKbFactory, ConfigKb]):
    """
    工作空间的配置预设，提供ConfigKb建造方法产生实例。
    """

    config_factory_cls = ConfigKbFactory

    def __init__(self):
        super().__init__()

    def _build_config_factory(self, config_json: Any) -> ConfigKbFactory:
        _config_factory = self.config_factory_cls()
        if config_json.get("DEFAULT_KNOWLEDGE_BASE"):
            _config_factory.DEFAULT_KNOWLEDGE_BASE = config_json.get(
                "DEFAULT_KNOWLEDGE_BASE"
            )
        if config_json.get("DEFAULT_VS_TYPE"):
            _config_factory.DEFAULT_VS_TYPE = config_json.get("DEFAULT_VS_TYPE")
        if config_json.get("CACHED_VS_NUM"):
            _config_factory.CACHED_VS_NUM = config_json.get("CACHED_VS_NUM")
        if config_json.get("CACHED_MEMO_VS_NUM"):
            _config_factory.CACHED_MEMO_VS_NUM = config_json.get("CACHED_MEMO_VS_NUM")
        if config_json.get("CHUNK_SIZE"):
            _config_factory.CHUNK_SIZE = config_json.get("CHUNK_SIZE")
        if config_json.get("OVERLAP_SIZE"):
            _config_factory.OVERLAP_SIZE = config_json.get("OVERLAP_SIZE")
        if config_json.get("VECTOR_SEARCH_TOP_K"):
            _config_factory.VECTOR_SEARCH_TOP_K = config_json.get("VECTOR_SEARCH_TOP_K")
        if config_json.get("SCORE_THRESHOLD"):
            _config_factory.SCORE_THRESHOLD = config_json.get("SCORE_THRESHOLD")
        if config_json.get("DEFAULT_SEARCH_ENGINE"):
            _config_factory.DEFAULT_SEARCH_ENGINE = config_json.get(
                "DEFAULT_SEARCH_ENGINE"
            )
        if config_json.get("SEARCH_ENGINE_TOP_K"):
            _config_factory.SEARCH_ENGINE_TOP_K = config_json.get("SEARCH_ENGINE_TOP_K")
        if config_json.get("ZH_TITLE_ENHANCE"):
            _config_factory.ZH_TITLE_ENHANCE = config_json.get("ZH_TITLE_ENHANCE")
        if config_json.get("PDF_OCR_THRESHOLD"):
            _config_factory.PDF_OCR_THRESHOLD = config_json.get("PDF_OCR_THRESHOLD")
        if config_json.get("KB_INFO"):
            _config_factory.KB_INFO = config_json.get("KB_INFO")
        if config_json.get("KB_ROOT_PATH"):
            _config_factory.KB_ROOT_PATH = config_json.get("KB_ROOT_PATH")
        if config_json.get("DB_ROOT_PATH"):
            _config_factory.DB_ROOT_PATH = config_json.get("DB_ROOT_PATH")
        if config_json.get("SQLALCHEMY_DATABASE_URI"):
            _config_factory.SQLALCHEMY_DATABASE_URI = config_json.get(
                "SQLALCHEMY_DATABASE_URI"
            )

        if config_json.get("TEXT_SPLITTER_NAME"):
            _config_factory.TEXT_SPLITTER_NAME = config_json.get("TEXT_SPLITTER_NAME")

        if config_json.get("EMBEDDING_KEYWORD_FILE"):
            _config_factory.EMBEDDING_KEYWORD_FILE = config_json.get(
                "EMBEDDING_KEYWORD_FILE"
            )

        return _config_factory

    @classmethod
    def get_type(cls) -> str:
        return ConfigKb.class_name()

    def get_config(self) -> ConfigKb:
        return self._config_factory.get_config()

    def set_default_knowledge_base(self, kb_name: str):
        self._config_factory.DEFAULT_KNOWLEDGE_BASE = kb_name
        self.store_config()

    def set_default_vs_type(self, vs_type: str):
        self._config_factory.DEFAULT_VS_TYPE = vs_type
        self.store_config()

    def set_cached_vs_num(self, cached_vs_num: int):
        self._config_factory.CACHED_VS_NUM = cached_vs_num
        self.store_config()

    def set_cached_memo_vs_num(self, cached_memo_vs_num: int):
        self._config_factory.CACHED_MEMO_VS_NUM = cached_memo_vs_num
        self.store_config()

    def set_chunk_size(self, chunk_size: int):
        self._config_factory.CHUNK_SIZE = chunk_size
        self.store_config()

    def set_overlap_size(self, overlap_size: int):
        self._config_factory.OVERLAP_SIZE = overlap_size
        self.store_config()

    def set_vector_search_top_k(self, vector_search_top_k: int):
        self._config_factory.VECTOR_SEARCH_TOP_K = vector_search_top_k
        self.store_config()

    def set_score_threshold(self, score_threshold: float):
        self._config_factory.SCORE_THRESHOLD = score_threshold
        self.store_config()

    def set_default_search_engine(self, default_search_engine: str):
        self._config_factory.DEFAULT_SEARCH_ENGINE = default_search_engine
        self.store_config()

    def set_search_engine_top_k(self, search_engine_top_k: int):
        self._config_factory.SEARCH_ENGINE_TOP_K = search_engine_top_k
        self.store_config()

    def set_zh_title_enhance(self, zh_title_enhance: bool):
        self._config_factory.ZH_TITLE_ENHANCE = zh_title_enhance
        self.store_config()

    def set_pdf_ocr_threshold(self, pdf_ocr_threshold: Tuple[float, float]):
        self._config_factory.PDF_OCR_THRESHOLD = pdf_ocr_threshold
        self.store_config()

    def set_kb_info(self, kb_info: Dict[str, str]):
        self._config_factory.KB_INFO = kb_info
        self.store_config()

    def set_kb_root_path(self, kb_root_path: str):
        self._config_factory.KB_ROOT_PATH = kb_root_path
        self.store_config()

    def set_db_root_path(self, db_root_path: str):
        self._config_factory.DB_ROOT_PATH = db_root_path
        self.store_config()

    def set_sqlalchemy_database_uri(self, sqlalchemy_database_uri: str):
        self._config_factory.SQLALCHEMY_DATABASE_URI = sqlalchemy_database_uri
        self.store_config()

    def set_text_splitter_name(self, text_splitter_name: str):
        self._config_factory.TEXT_SPLITTER_NAME = text_splitter_name
        self.store_config()

    def set_embedding_keyword_file(self, embedding_keyword_file: str):
        self._config_factory.EMBEDDING_KEYWORD_FILE = embedding_keyword_file
        self.store_config()


config_kb_workspace: ConfigKbWorkSpace = ConfigKbWorkSpace()

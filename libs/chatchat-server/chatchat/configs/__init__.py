import importlib
import importlib.util
import os
from pathlib import Path
from typing import Dict, Any

import json
import logging

logger = logging.getLogger()


def _load_mod(mod, attr):
    attr_cfg = None
    for name, obj in vars(mod).items():
        if name == attr:
            attr_cfg = obj
            break

    if attr_cfg is None:
        logger.warning(
            f"Missing attr_cfg:{attr} in {mod}, Skip."
        )
        return attr_cfg
    return attr_cfg


def _import_config_mod_load(import_config_mod: str) -> Dict:
    # 加载用户空间的配置
    user_config_path = os.path.join(os.path.expanduser("~"), ".config", "chatchat/configs")
    user_import = True  # 默认加载用户配置
    if os.path.exists(user_config_path):
        try:

            file_names = os.listdir(user_config_path)

            if import_config_mod + ".py" not in file_names:
                logger.warning(
                    f"Missing {file_names}.py file in {user_config_path}, Skip."
                )
                user_import = False
            if user_import:
                # Dynamic loading {config}.py file
                py_path = os.path.join(user_config_path, import_config_mod + ".py")
                spec = importlib.util.spec_from_file_location(
                    f"*",
                    py_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                return {
                    "user_import": user_import,
                    "user_config_path": user_config_path,
                    "load_mod": _load_mod,
                    "module": module,
                }

        except ImportError as e:
            logger.error(
                f"Failed to load user config from {user_config_path}, Skip.", e
            )
            pass
    else:
        user_import = False

    if user_import:
        logger.error(
            f"Failed to load user config from {user_config_path}, Skip."
        )
        raise RuntimeError(f"Failed to load user config from {user_config_path}")
    # 当前文件路径
    py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), import_config_mod + ".py")

    spec = importlib.util.spec_from_file_location(f"*",
                                                  py_path)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return {
        "user_import": user_import,
        "user_config_path": user_config_path,
        "load_mod": _load_mod,
        "module": module,
    }


CONFIG_IMPORTS = {

    "_basic_config.py": _import_config_mod_load("_basic_config"),
    "_kb_config.py": _import_config_mod_load("_kb_config"),
    "_model_config.py": _import_config_mod_load("_model_config"),
    "_prompt_config.py": _import_config_mod_load("_prompt_config"),
    "_server_config.py": _import_config_mod_load("_server_config"),
}


def _import_ConfigBasic() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")
    ConfigBasic = load_mod(basic_config_load.get("module"), "ConfigBasic")

    return ConfigBasic


def _import_ConfigBasicFactory() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")
    ConfigBasicFactory = load_mod(basic_config_load.get("module"), "ConfigBasicFactory")

    return ConfigBasicFactory


def _import_ConfigBasicWorkSpace() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")
    ConfigBasicWorkSpace = load_mod(basic_config_load.get("module"), "ConfigBasicWorkSpace")

    return ConfigBasicWorkSpace


def _import_config_basic_workspace() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")
    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")
    return config_basic_workspace


def _import_log_verbose() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")
    return config_basic_workspace.get_config().log_verbose


def _import_chatchat_root() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")

    return config_basic_workspace.get_config().CHATCHAT_ROOT


def _import_data_path() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")
    return config_basic_workspace.get_config().DATA_PATH


def _import_img_dir() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")

    return config_basic_workspace.get_config().IMG_DIR


def _import_nltk_data_path() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")
    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")

    return config_basic_workspace.get_config().NLTK_DATA_PATH


def _import_log_format() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")

    return config_basic_workspace.get_config().LOG_FORMAT


def _import_log_path() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")

    return config_basic_workspace.get_config().LOG_PATH


def _import_media_path() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")

    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")

    return config_basic_workspace.get_config().MEDIA_PATH


def _import_base_temp_dir() -> Any:
    basic_config_load = CONFIG_IMPORTS.get("_basic_config.py")
    load_mod = basic_config_load.get("load_mod")
    config_basic_workspace = load_mod(basic_config_load.get("module"), "config_basic_workspace")
    return config_basic_workspace.get_config().BASE_TEMP_DIR


def _import_default_knowledge_base() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    DEFAULT_KNOWLEDGE_BASE = load_mod(kb_config_load.get("module"), "DEFAULT_KNOWLEDGE_BASE")

    return DEFAULT_KNOWLEDGE_BASE


def _import_default_vs_type() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    DEFAULT_VS_TYPE = load_mod(kb_config_load.get("module"), "DEFAULT_VS_TYPE")

    return DEFAULT_VS_TYPE


def _import_cached_vs_num() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    CACHED_VS_NUM = load_mod(kb_config_load.get("module"), "CACHED_VS_NUM")

    return CACHED_VS_NUM


def _import_cached_memo_vs_num() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    CACHED_MEMO_VS_NUM = load_mod(kb_config_load.get("module"), "CACHED_MEMO_VS_NUM")

    return CACHED_MEMO_VS_NUM


def _import_chunk_size() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    CHUNK_SIZE = load_mod(kb_config_load.get("module"), "CHUNK_SIZE")

    return CHUNK_SIZE


def _import_overlap_size() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    OVERLAP_SIZE = load_mod(kb_config_load.get("module"), "OVERLAP_SIZE")

    return OVERLAP_SIZE


def _import_vector_search_top_k() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    VECTOR_SEARCH_TOP_K = load_mod(kb_config_load.get("module"), "VECTOR_SEARCH_TOP_K")

    return VECTOR_SEARCH_TOP_K


def _import_score_threshold() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    SCORE_THRESHOLD = load_mod(kb_config_load.get("module"), "SCORE_THRESHOLD")

    return SCORE_THRESHOLD


def _import_default_search_engine() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    DEFAULT_SEARCH_ENGINE = load_mod(kb_config_load.get("module"), "DEFAULT_SEARCH_ENGINE")

    return DEFAULT_SEARCH_ENGINE


def _import_search_engine_top_k() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    SEARCH_ENGINE_TOP_K = load_mod(kb_config_load.get("module"), "SEARCH_ENGINE_TOP_K")

    return SEARCH_ENGINE_TOP_K


def _import_zh_title_enhance() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    ZH_TITLE_ENHANCE = load_mod(kb_config_load.get("module"), "ZH_TITLE_ENHANCE")

    return ZH_TITLE_ENHANCE


def _import_pdf_ocr_threshold() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    PDF_OCR_THRESHOLD = load_mod(kb_config_load.get("module"), "PDF_OCR_THRESHOLD")

    return PDF_OCR_THRESHOLD


def _import_kb_info() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    KB_INFO = load_mod(kb_config_load.get("module"), "KB_INFO")

    return KB_INFO


def _import_kb_root_path() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    KB_ROOT_PATH = load_mod(kb_config_load.get("module"), "KB_ROOT_PATH")

    return KB_ROOT_PATH


def _import_db_root_path() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    DB_ROOT_PATH = load_mod(kb_config_load.get("module"), "DB_ROOT_PATH")

    return DB_ROOT_PATH


def _import_sqlalchemy_database_uri() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    SQLALCHEMY_DATABASE_URI = load_mod(kb_config_load.get("module"), "SQLALCHEMY_DATABASE_URI")

    return SQLALCHEMY_DATABASE_URI


def _import_kbs_config() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    kbs_config = load_mod(kb_config_load.get("module"), "kbs_config")

    return kbs_config


def _import_text_splitter_dict() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    text_splitter_dict = load_mod(kb_config_load.get("module"), "text_splitter_dict")

    return text_splitter_dict


def _import_text_splitter_name() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    TEXT_SPLITTER_NAME = load_mod(kb_config_load.get("module"), "TEXT_SPLITTER_NAME")

    return TEXT_SPLITTER_NAME


def _import_embedding_keyword_file() -> Any:
    kb_config_load = CONFIG_IMPORTS.get("_kb_config.py")
    load_mod = kb_config_load.get("load_mod")
    EMBEDDING_KEYWORD_FILE = load_mod(kb_config_load.get("module"), "EMBEDDING_KEYWORD_FILE")

    return EMBEDDING_KEYWORD_FILE


def _import_default_llm_model() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    DEFAULT_LLM_MODEL = load_mod(model_config_load.get("module"), "DEFAULT_LLM_MODEL")

    return DEFAULT_LLM_MODEL


def _import_default_embedding_model() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    DEFAULT_EMBEDDING_MODEL = load_mod(model_config_load.get("module"), "DEFAULT_EMBEDDING_MODEL")

    return DEFAULT_EMBEDDING_MODEL


def _import_agent_model() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    Agent_MODEL = load_mod(model_config_load.get("module"), "Agent_MODEL")

    return Agent_MODEL


def _import_history_len() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    HISTORY_LEN = load_mod(model_config_load.get("module"), "HISTORY_LEN")

    return HISTORY_LEN


def _import_max_tokens() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    MAX_TOKENS = load_mod(model_config_load.get("module"), "MAX_TOKENS")

    return MAX_TOKENS


def _import_temperature() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    TEMPERATURE = load_mod(model_config_load.get("module"), "TEMPERATURE")

    return TEMPERATURE


def _import_support_agent_models() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    SUPPORT_AGENT_MODELS = load_mod(model_config_load.get("module"), "SUPPORT_AGENT_MODELS")

    return SUPPORT_AGENT_MODELS


def _import_llm_model_config() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    LLM_MODEL_CONFIG = load_mod(model_config_load.get("module"), "LLM_MODEL_CONFIG")

    return LLM_MODEL_CONFIG


def _import_model_platforms() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    MODEL_PLATFORMS = load_mod(model_config_load.get("module"), "MODEL_PLATFORMS")

    return MODEL_PLATFORMS


def _import_model_providers_cfg_path() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    MODEL_PROVIDERS_CFG_PATH_CONFIG = load_mod(model_config_load.get("module"), "MODEL_PROVIDERS_CFG_PATH_CONFIG")

    return MODEL_PROVIDERS_CFG_PATH_CONFIG


def _import_model_providers_cfg_host() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    MODEL_PROVIDERS_CFG_HOST = load_mod(model_config_load.get("module"), "MODEL_PROVIDERS_CFG_HOST")

    return MODEL_PROVIDERS_CFG_HOST


def _import_model_providers_cfg_port() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    MODEL_PROVIDERS_CFG_PORT = load_mod(model_config_load.get("module"), "MODEL_PROVIDERS_CFG_PORT")

    return MODEL_PROVIDERS_CFG_PORT


def _import_tool_config() -> Any:
    model_config_load = CONFIG_IMPORTS.get("_model_config.py")
    load_mod = model_config_load.get("load_mod")
    TOOL_CONFIG = load_mod(model_config_load.get("module"), "TOOL_CONFIG")

    return TOOL_CONFIG


def _import_prompt_templates() -> Any:
    prompt_config_load = CONFIG_IMPORTS.get("_prompt_config.py")
    load_mod = prompt_config_load.get("load_mod")
    PROMPT_TEMPLATES = load_mod(prompt_config_load.get("module"), "PROMPT_TEMPLATES")

    return PROMPT_TEMPLATES


def _import_httpx_default_timeout() -> Any:
    server_config_load = CONFIG_IMPORTS.get("_server_config.py")
    load_mod = server_config_load.get("load_mod")
    HTTPX_DEFAULT_TIMEOUT = load_mod(server_config_load.get("module"), "HTTPX_DEFAULT_TIMEOUT")

    return HTTPX_DEFAULT_TIMEOUT


def _import_open_cross_domain() -> Any:
    server_config_load = CONFIG_IMPORTS.get("_server_config.py")
    load_mod = server_config_load.get("load_mod")
    OPEN_CROSS_DOMAIN = load_mod(server_config_load.get("module"), "OPEN_CROSS_DOMAIN")

    return OPEN_CROSS_DOMAIN


def _import_default_bind_host() -> Any:
    server_config_load = CONFIG_IMPORTS.get("_server_config.py")
    load_mod = server_config_load.get("load_mod")
    DEFAULT_BIND_HOST = load_mod(server_config_load.get("module"), "DEFAULT_BIND_HOST")

    return DEFAULT_BIND_HOST


def _import_webui_server() -> Any:
    server_config_load = CONFIG_IMPORTS.get("_server_config.py")
    load_mod = server_config_load.get("load_mod")
    WEBUI_SERVER = load_mod(server_config_load.get("module"), "WEBUI_SERVER")

    return WEBUI_SERVER


def _import_api_server() -> Any:
    server_config_load = CONFIG_IMPORTS.get("_server_config.py")
    load_mod = server_config_load.get("load_mod")
    API_SERVER = load_mod(server_config_load.get("module"), "API_SERVER")

    return API_SERVER


def __getattr__(name: str) -> Any:
    if name == "ConfigBasic":
        return _import_ConfigBasic()
    elif name == "ConfigBasicFactory":
        return _import_ConfigBasicFactory()
    elif name == "ConfigBasicWorkSpace":
        return _import_ConfigBasicWorkSpace()
    elif name == "config_basic_workspace":
        return _import_config_basic_workspace()
    elif name == "log_verbose":
        return _import_log_verbose()
    elif name == "CHATCHAT_ROOT":
        return _import_chatchat_root()
    elif name == "DATA_PATH":
        return _import_data_path()
    elif name == "IMG_DIR":
        return _import_img_dir()
    elif name == "NLTK_DATA_PATH":
        return _import_nltk_data_path()
    elif name == "LOG_FORMAT":
        return _import_log_format()
    elif name == "LOG_PATH":
        return _import_log_path()
    elif name == "MEDIA_PATH":
        return _import_media_path()
    elif name == "BASE_TEMP_DIR":
        return _import_base_temp_dir()
    elif name == "DEFAULT_KNOWLEDGE_BASE":
        return _import_default_knowledge_base()
    elif name == "DEFAULT_VS_TYPE":
        return _import_default_vs_type()
    elif name == "CACHED_VS_NUM":
        return _import_cached_vs_num()
    elif name == "CACHED_MEMO_VS_NUM":
        return _import_cached_memo_vs_num()
    elif name == "CHUNK_SIZE":
        return _import_chunk_size()
    elif name == "OVERLAP_SIZE":
        return _import_overlap_size()
    elif name == "VECTOR_SEARCH_TOP_K":
        return _import_vector_search_top_k()
    elif name == "SCORE_THRESHOLD":
        return _import_score_threshold()
    elif name == "DEFAULT_SEARCH_ENGINE":
        return _import_default_search_engine()
    elif name == "SEARCH_ENGINE_TOP_K":
        return _import_search_engine_top_k()
    elif name == "ZH_TITLE_ENHANCE":
        return _import_zh_title_enhance()
    elif name == "PDF_OCR_THRESHOLD":
        return _import_pdf_ocr_threshold()
    elif name == "KB_INFO":
        return _import_kb_info()
    elif name == "KB_ROOT_PATH":
        return _import_kb_root_path()
    elif name == "DB_ROOT_PATH":
        return _import_db_root_path()
    elif name == "SQLALCHEMY_DATABASE_URI":
        return _import_sqlalchemy_database_uri()
    elif name == "kbs_config":
        return _import_kbs_config()
    elif name == "text_splitter_dict":
        return _import_text_splitter_dict()
    elif name == "TEXT_SPLITTER_NAME":
        return _import_text_splitter_name()
    elif name == "EMBEDDING_KEYWORD_FILE":
        return _import_embedding_keyword_file()
    elif name == "DEFAULT_LLM_MODEL":
        return _import_default_llm_model()
    elif name == "DEFAULT_EMBEDDING_MODEL":
        return _import_default_embedding_model()
    elif name == "Agent_MODEL":
        return _import_agent_model()
    elif name == "HISTORY_LEN":
        return _import_history_len()
    elif name == "MAX_TOKENS":
        return _import_max_tokens()
    elif name == "TEMPERATURE":
        return _import_temperature()
    elif name == "SUPPORT_AGENT_MODELS":
        return _import_support_agent_models()
    elif name == "LLM_MODEL_CONFIG":
        return _import_llm_model_config()
    elif name == "MODEL_PLATFORMS":
        return _import_model_platforms()
    elif name == "MODEL_PROVIDERS_CFG_PATH_CONFIG":
        return _import_model_providers_cfg_path()
    elif name == "MODEL_PROVIDERS_CFG_HOST":
        return _import_model_providers_cfg_host()
    elif name == "MODEL_PROVIDERS_CFG_PORT":
        return _import_model_providers_cfg_port()
    elif name == "TOOL_CONFIG":
        return _import_tool_config()
    elif name == "PROMPT_TEMPLATES":
        return _import_prompt_templates()
    elif name == "HTTPX_DEFAULT_TIMEOUT":
        return _import_httpx_default_timeout()
    elif name == "OPEN_CROSS_DOMAIN":
        return _import_default_bind_host()
    elif name == "WEBUI_SERVER":
        return _import_webui_server()
    elif name == "API_SERVER":
        return _import_api_server()


VERSION = "v0.3.0-preview"

__all__ = [
    "VERSION",
    "config_basic_workspace",
    "log_verbose",
    "CHATCHAT_ROOT",
    "DATA_PATH",
    "IMG_DIR",
    "NLTK_DATA_PATH",
    "LOG_FORMAT",
    "LOG_PATH",
    "MEDIA_PATH",
    "BASE_TEMP_DIR",
    "DEFAULT_KNOWLEDGE_BASE",
    "DEFAULT_VS_TYPE",
    "CACHED_VS_NUM",
    "CACHED_MEMO_VS_NUM",
    "CHUNK_SIZE",
    "OVERLAP_SIZE",
    "VECTOR_SEARCH_TOP_K",
    "SCORE_THRESHOLD",
    "DEFAULT_SEARCH_ENGINE",
    "SEARCH_ENGINE_TOP_K",
    "ZH_TITLE_ENHANCE",
    "PDF_OCR_THRESHOLD",
    "KB_INFO",
    "KB_ROOT_PATH",
    "DB_ROOT_PATH",
    "SQLALCHEMY_DATABASE_URI",
    "kbs_config",
    "text_splitter_dict",
    "TEXT_SPLITTER_NAME",
    "EMBEDDING_KEYWORD_FILE",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_EMBEDDING_MODEL",
    "Agent_MODEL",
    "HISTORY_LEN",
    "MAX_TOKENS",
    "TEMPERATURE",
    "SUPPORT_AGENT_MODELS",
    "LLM_MODEL_CONFIG",
    "MODEL_PLATFORMS",
    "MODEL_PROVIDERS_CFG_PATH_CONFIG",
    "MODEL_PROVIDERS_CFG_HOST",
    "MODEL_PROVIDERS_CFG_PORT",
    "TOOL_CONFIG",
    "PROMPT_TEMPLATES",
    "HTTPX_DEFAULT_TIMEOUT",
    "OPEN_CROSS_DOMAIN",
    "WEBUI_SERVER",
    "API_SERVER",

    "ConfigBasic",
    "ConfigBasicFactory",
    "ConfigBasicWorkSpace",

]

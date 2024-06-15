from pathlib import Path

from chatchat.configs import (
    ConfigBasicFactory,
    ConfigBasic,
    ConfigBasicWorkSpace,
    ConfigModelWorkSpace,
    ConfigModel,
    ConfigServerWorkSpace,
    ConfigServer,
    ConfigKbWorkSpace,
    ConfigKb,
)
import os


def test_config_basic_workspace():
    config_basic_workspace: ConfigBasicWorkSpace = ConfigBasicWorkSpace()
    assert config_basic_workspace.get_config() is not None
    base_root = os.path.join(Path(__file__).absolute().parent, "chatchat")
    config_basic_workspace.set_data_path(os.path.join(base_root, "data"))
    config_basic_workspace.set_log_verbose(True)
    config_basic_workspace.set_log_format(" %(message)s")

    config: ConfigBasic = config_basic_workspace.get_config()
    assert config.log_verbose is True
    assert config.DATA_PATH == os.path.join(base_root, "data")
    assert config.IMG_DIR is not None
    assert config.NLTK_DATA_PATH == os.path.join(base_root, "data", "nltk_data")
    assert config.LOG_FORMAT == " %(message)s"
    assert config.LOG_PATH == os.path.join(base_root, "data", "logs")
    assert config.MEDIA_PATH == os.path.join(base_root, "data", "media")

    assert os.path.exists(os.path.join(config.MEDIA_PATH, "image"))
    assert os.path.exists(os.path.join(config.MEDIA_PATH, "audio"))
    assert os.path.exists(os.path.join(config.MEDIA_PATH, "video"))
    config_basic_workspace.clear()


def test_workspace_default():
    from chatchat.configs import (log_verbose, DATA_PATH, IMG_DIR, NLTK_DATA_PATH, LOG_FORMAT, LOG_PATH, MEDIA_PATH)
    assert log_verbose is False
    assert DATA_PATH is not None
    assert IMG_DIR is not None
    assert NLTK_DATA_PATH is not None
    assert LOG_FORMAT is not None
    assert LOG_PATH is not None
    assert MEDIA_PATH is not None


def test_config_model_workspace():

    config_model_workspace: ConfigModelWorkSpace = ConfigModelWorkSpace()

    assert config_model_workspace.get_config() is not None

    config_model_workspace.set_default_llm_model(llm_model="glm4-chat")
    config_model_workspace.set_default_embedding_model(embedding_model="text1")
    config_model_workspace.set_agent_model(agent_model="agent")
    config_model_workspace.set_history_len(history_len=1)
    config_model_workspace.set_max_tokens(max_tokens=1000)
    config_model_workspace.set_temperature(temperature=0.1)
    config_model_workspace.set_support_agent_models(support_agent_models=["glm4-chat"])
    config_model_workspace.set_model_providers_cfg_path_config(model_providers_cfg_path_config="model_providers.yaml")
    config_model_workspace.set_model_providers_cfg_host(model_providers_cfg_host="127.0.0.1")
    config_model_workspace.set_model_providers_cfg_port(model_providers_cfg_port=8000)

    config: ConfigModel = config_model_workspace.get_config()

    assert config.DEFAULT_LLM_MODEL == "glm4-chat"
    assert config.DEFAULT_EMBEDDING_MODEL == "text1"
    assert config.Agent_MODEL == "agent"
    assert config.HISTORY_LEN == 1
    assert config.MAX_TOKENS == 1000
    assert config.TEMPERATURE == 0.1
    assert config.SUPPORT_AGENT_MODELS == ["glm4-chat"]
    assert config.MODEL_PROVIDERS_CFG_PATH_CONFIG == "model_providers.yaml"
    assert config.MODEL_PROVIDERS_CFG_HOST == "127.0.0.1"
    assert config.MODEL_PROVIDERS_CFG_PORT == 8000
    config_model_workspace.clear()


def test_model_config():
    from chatchat.configs import (
        DEFAULT_LLM_MODEL, DEFAULT_EMBEDDING_MODEL, Agent_MODEL, HISTORY_LEN, MAX_TOKENS, TEMPERATURE,
        SUPPORT_AGENT_MODELS, MODEL_PROVIDERS_CFG_PATH_CONFIG, MODEL_PROVIDERS_CFG_HOST, MODEL_PROVIDERS_CFG_PORT,
        TOOL_CONFIG, MODEL_PLATFORMS, LLM_MODEL_CONFIG
    )
    assert DEFAULT_LLM_MODEL is not None
    assert DEFAULT_EMBEDDING_MODEL is not None
    assert Agent_MODEL is None
    assert HISTORY_LEN is not None
    assert MAX_TOKENS is None
    assert TEMPERATURE is not None
    assert SUPPORT_AGENT_MODELS is not None
    assert MODEL_PROVIDERS_CFG_PATH_CONFIG is not None
    assert MODEL_PROVIDERS_CFG_HOST is not None
    assert MODEL_PROVIDERS_CFG_PORT is not None
    assert TOOL_CONFIG is not None
    assert MODEL_PLATFORMS is not None
    assert LLM_MODEL_CONFIG is not None


def test_config_server_workspace():
    config_server_workspace: ConfigServerWorkSpace = ConfigServerWorkSpace()

    assert config_server_workspace.get_config() is not None

    config_server_workspace.set_httpx_default_timeout(timeout=10)
    config_server_workspace.set_open_cross_domain(open_cross_domain=True)
    config_server_workspace.set_default_bind_host(default_bind_host="0.0.0.0")
    config_server_workspace.set_webui_server_port(webui_server_port=8000)
    config_server_workspace.set_api_server_port(api_server_port=8001)

    config: ConfigServer = config_server_workspace.get_config()

    assert config.HTTPX_DEFAULT_TIMEOUT == 10
    assert config.OPEN_CROSS_DOMAIN is True
    assert config.DEFAULT_BIND_HOST == "0.0.0.0"
    assert config.WEBUI_SERVER_PORT == 8000
    assert config.API_SERVER_PORT == 8001
    config_server_workspace.clear()


def test_server_config():
    from chatchat.configs import (
        HTTPX_DEFAULT_TIMEOUT, OPEN_CROSS_DOMAIN, DEFAULT_BIND_HOST,
        WEBUI_SERVER, API_SERVER
    )
    assert HTTPX_DEFAULT_TIMEOUT is not None
    assert OPEN_CROSS_DOMAIN is not None
    assert DEFAULT_BIND_HOST is not None
    assert WEBUI_SERVER is not None
    assert API_SERVER is not None


def test_config_kb_workspace():

    config_kb_workspace: ConfigKbWorkSpace = ConfigKbWorkSpace()

    assert config_kb_workspace.get_config() is not None

    config_kb_workspace.set_default_knowledge_base(kb_name="test")
    config_kb_workspace.set_default_vs_type(vs_type="tes")
    config_kb_workspace.set_cached_vs_num(cached_vs_num=10)
    config_kb_workspace.set_cached_memo_vs_num(cached_memo_vs_num=10)
    config_kb_workspace.set_chunk_size(chunk_size=10)
    config_kb_workspace.set_overlap_size(overlap_size=10)
    config_kb_workspace.set_vector_search_top_k(vector_search_top_k=10)
    config_kb_workspace.set_score_threshold(score_threshold=0.1)
    config_kb_workspace.set_default_search_engine(default_search_engine="test")
    config_kb_workspace.set_search_engine_top_k(search_engine_top_k=10)
    config_kb_workspace.set_zh_title_enhance(zh_title_enhance=True)
    config_kb_workspace.set_pdf_ocr_threshold(pdf_ocr_threshold=(0.1, 0.2))
    config_kb_workspace.set_kb_info(kb_info={
        "samples": "关于本项目issue的解答",
    })
    config_kb_workspace.set_kb_root_path(kb_root_path="test")
    config_kb_workspace.set_db_root_path(db_root_path="test")
    config_kb_workspace.set_sqlalchemy_database_uri(sqlalchemy_database_uri="test")
    config_kb_workspace.set_text_splitter_name(text_splitter_name="test")
    config_kb_workspace.set_embedding_keyword_file(embedding_keyword_file="test")

    config: ConfigKb = config_kb_workspace.get_config()
    assert config.DEFAULT_KNOWLEDGE_BASE == "test"
    assert config.DEFAULT_VS_TYPE == "tes"
    assert config.CACHED_VS_NUM == 10
    assert config.CACHED_MEMO_VS_NUM == 10
    assert config.CHUNK_SIZE == 10
    assert config.OVERLAP_SIZE == 10
    assert config.VECTOR_SEARCH_TOP_K == 10
    assert config.SCORE_THRESHOLD == 0.1
    assert config.DEFAULT_SEARCH_ENGINE == "test"
    assert config.SEARCH_ENGINE_TOP_K == 10
    assert config.ZH_TITLE_ENHANCE is True
    assert config.PDF_OCR_THRESHOLD == (0.1, 0.2)
    assert config.KB_INFO == {
        "samples": "关于本项目issue的解答",
    }
    assert config.KB_ROOT_PATH == "test"
    assert config.DB_ROOT_PATH == "test"
    assert config.SQLALCHEMY_DATABASE_URI == "test"
    assert config.TEXT_SPLITTER_NAME == "test"
    assert config.EMBEDDING_KEYWORD_FILE == "test"
    config_kb_workspace.clear()



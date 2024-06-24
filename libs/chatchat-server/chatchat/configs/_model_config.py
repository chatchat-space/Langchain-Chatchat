import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).parent))
import _core_config as core_config

logger = logging.getLogger()


class ConfigModel(core_config.Config):
    DEFAULT_LLM_MODEL: Optional[str] = None
    """默认选用的 LLM 名称"""
    DEFAULT_EMBEDDING_MODEL: Optional[str] = None
    """默认选用的 Embedding 名称"""
    Agent_MODEL: Optional[str] = None
    """AgentLM模型的名称 (可以不指定，指定之后就锁定进入Agent之后的Chain的模型，不指定就是LLM_MODELS[0])"""
    HISTORY_LEN: Optional[int] = None
    """历史对话轮数"""
    MAX_TOKENS: Optional[int] = None
    """大模型最长支持的长度，如果不填写，则使用模型默认的最大长度，如果填写，则为用户设定的最大长度"""
    TEMPERATURE: Optional[float] = None
    """LLM通用对话参数"""
    SUPPORT_AGENT_MODELS: Optional[List[str]] = None
    """支持的Agent模型"""
    LLM_MODEL_CONFIG: Optional[Dict[str, Dict[str, Any]]] = None
    """LLM模型配置，包括了不同模态初始化参数"""
    MODEL_PLATFORMS: Optional[List[Dict[str, Any]]] = None
    """模型平台配置"""
    TOOL_CONFIG: Optional[Dict[str, Any]] = None
    """工具配置项"""

    @classmethod
    def class_name(cls) -> str:
        return cls.__name__

    def __str__(self):
        return self.to_json()


@dataclass
class ConfigModelFactory(core_config.ConfigFactory[ConfigModel]):
    """ConfigModel工厂类"""

    def __init__(self):
        # 默认选用的 LLM 名称
        self.DEFAULT_LLM_MODEL = "glm4-chat"

        # 默认选用的 Embedding 名称
        self.DEFAULT_EMBEDDING_MODEL = "bge-large-zh-v1.5"

        # AgentLM模型的名称 (可以不指定，指定之后就锁定进入Agent之后的Chain的模型，不指定就是LLM_MODELS[0])
        self.Agent_MODEL = None

        # 历史对话轮数
        self.HISTORY_LEN = 3

        # 大模型最长支持的长度，如果不填写，则使用模型默认的最大长度，如果填写，则为用户设定的最大长度
        self.MAX_TOKENS = None

        # LLM通用对话参数
        self.TEMPERATURE = 0.7
        # TOP_P = 0.95 # ChatOpenAI暂不支持该参数

        self.SUPPORT_AGENT_MODELS = [
            "chatglm3-6b",
            "openai-api",
            "Qwen-14B-Chat",
            "Qwen-7B-Chat",
            "qwen-turbo",
        ]

        #   ### 如果您已经有了一个openai endpoint的能力的地址，可以在这里直接配置
        #   - platform_name 可以任意填写，不要重复即可
        #   - platform_type 以后可能根据平台类型做一些功能区分,与platform_name一致即可
        #   - 将框架部署的模型填写到对应列表即可。不同框架可以加载同名模型，项目会自动做负载均衡。

        # 创建一个全局的共享字典
        self.MODEL_PLATFORMS = [
            {
                "platform_name": "oneapi",
                "platform_type": "oneapi",
                "api_base_url": "http://127.0.0.1:3000/v1",
                "api_key": "sk-",
                "api_concurrencies": 5,
                "llm_models": [
                    # 智谱 API
                    "chatglm_pro",
                    "chatglm_turbo",
                    "chatglm_std",
                    "chatglm_lite",
                    # 千问 API
                    "qwen-turbo",
                    "qwen-plus",
                    "qwen-max",
                    "qwen-max-longcontext",
                    # 千帆 API
                    "ERNIE-Bot",
                    "ERNIE-Bot-turbo",
                    "ERNIE-Bot-4",
                    # 星火 API
                    "SparkDesk",
                ],
                "embed_models": [
                    # 千问 API
                    "text-embedding-v1",
                    # 千帆 API
                    "Embedding-V1",
                ],
                "image_models": [],
                "reranking_models": [],
                "speech2text_models": [],
                "tts_models": [],
            },
            {
                "platform_name": "xinference",
                "platform_type": "xinference",
                "api_base_url": "http://127.0.0.1:9997/v1",
                "api_key": "EMPT",
                "api_concurrencies": 5,
                "llm_models": [
                    "chatglm3",
                    "glm4-chat",
                    "qwen1.5-chat",
                    "qwen2-instruct",
                ],
                "embed_models": [
                    "bge-large-zh-v1.5",
                ],
                "image_models": [],
                "reranking_models": [],
                "speech2text_models": [],
                "tts_models": [],
            },
        ]
        # 工具配置项
        self.TOOL_CONFIG = {
            "search_local_knowledgebase": {
                "use": False,
                "top_k": 3,
                "score_threshold": 1.0,
                "conclude_prompt": {
                    "with_result": '<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 "根据已知信息无法回答该问题"，'
                    "不允许在答案中添加编造成分，答案请使用中文。 </指令>\n"
                    "<已知信息>{{ context }}</已知信息>\n"
                    "<问题>{{ question }}</问题>\n",
                    "without_result": "请你根据我的提问回答我的问题:\n"
                    "{{ question }}\n"
                    "请注意，你必须在回答结束后强调，你的回答是根据你的经验回答而不是参考资料回答的。\n",
                },
            },
            "search_internet": {
                "use": False,
                "search_engine_name": "bing",
                "search_engine_config": {
                    "bing": {
                        "result_len": 3,
                        "bing_search_url": "https://api.bing.microsoft.com/v7.0/search",
                        "bing_key": "",
                    },
                    "metaphor": {
                        "result_len": 3,
                        "metaphor_api_key": "",
                        "split_result": False,
                        "chunk_size": 500,
                        "chunk_overlap": 0,
                    },
                    "duckduckgo": {"result_len": 3},
                },
                "top_k": 10,
                "verbose": "Origin",
                "conclude_prompt": "<指令>这是搜索到的互联网信息，请你根据这些信息进行提取并有调理，简洁的回答问题。如果无法从中得到答案，请说 “无法搜索到能回答问题的内容”。 "
                "</指令>\n<已知信息>{{ context }}</已知信息>\n"
                "<问题>\n"
                "{{ question }}\n"
                "</问题>\n",
            },
            "arxiv": {
                "use": False,
            },
            "shell": {
                "use": False,
            },
            "weather_check": {
                "use": False,
                "api_key": "S8vrB4U_-c5mvAMiK",
            },
            "search_youtube": {
                "use": False,
            },
            "wolfram": {
                "use": False,
                "appid": "",
            },
            "calculate": {
                "use": False,
            },
            "vqa_processor": {
                "use": False,
                "model_path": "your model path",
                "tokenizer_path": "your tokenizer path",
                "device": "cuda:1",
            },
            "aqa_processor": {
                "use": False,
                "model_path": "your model path",
                "tokenizer_path": "yout tokenizer path",
                "device": "cuda:2",
            },
            "text2images": {
                "use": False,
            },
            # text2sql使用建议
            # 1、因大模型生成的sql可能与预期有偏差，请务必在测试环境中进行充分测试、评估；
            # 2、生产环境中，对于查询操作，由于不确定查询效率，推荐数据库采用主从数据库架构，让text2sql连接从数据库，防止可能的慢查询影响主业务；
            # 3、对于写操作应保持谨慎，如不需要写操作，设置read_only为True,最好再从数据库层面收回数据库用户的写权限，防止用户通过自然语言对数据库进行修改操作；
            # 4、text2sql与大模型在意图理解、sql转换等方面的能力有关，可切换不同大模型进行测试；
            # 5、数据库表名、字段名应与其实际作用保持一致、容易理解，且应对数据库表名、字段进行详细的备注说明，帮助大模型更好理解数据库结构；
            # 6、若现有数据库表名难于让大模型理解，可配置下面table_comments字段，补充说明某些表的作用。
            "text2sql": {
                "use": False,
                # SQLAlchemy连接字符串，支持的数据库有：
                # crate、duckdb、googlesql、mssql、mysql、mariadb、oracle、postgresql、sqlite、clickhouse、prestodb
                # 不同的数据库请查询SQLAlchemy，修改sqlalchemy_connect_str，配置对应的数据库连接，如sqlite为sqlite:///数据库文件路径，下面示例为mysql
                # 如提示缺少对应数据库的驱动，请自行通过poetry安装
                "sqlalchemy_connect_str": "mysql+pymysql://用户名:密码@主机地址/数据库名称e",
                # 务必评估是否需要开启read_only,开启后会对sql语句进行检查，请确认text2sql.py中的intercept_sql拦截器是否满足你使用的数据库只读要求
                # 优先推荐从数据库层面对用户权限进行限制
                "read_only": False,
                # 限定返回的行数
                "top_k": 50,
                # 是否返回中间步骤
                "return_intermediate_steps": True,
                # 如果想指定特定表，请填写表名称，如["sys_user","sys_dept"]，不填写走智能判断应该使用哪些表
                "table_names": [],
                # 对表名进行额外说明，辅助大模型更好的判断应该使用哪些表，尤其是SQLDatabaseSequentialChain模式下,是根据表名做的预测，很容易误判。
                "table_comments": {
                    # 如果出现大模型选错表的情况，可尝试根据实际情况填写表名和说明
                    # "tableA":"这是一个用户表，存储了用户的基本信息",
                    # "tanleB":"角色表",
                },
            },
        }
        self._init_llm_work_config()

    def _init_llm_work_config(self):
        """初始化知识库runtime的一些配置"""

        self.LLM_MODEL_CONFIG = {
            # 意图识别不需要输出，模型后台知道就行
            "preprocess_model": {
                self.DEFAULT_LLM_MODEL: {
                    "temperature": 0.05,
                    "max_tokens": 4096,
                    "history_len": 100,
                    "prompt_name": "default",
                    "callbacks": False,
                },
            },
            "llm_model": {
                self.DEFAULT_LLM_MODEL: {
                    "temperature": 0.9,
                    "max_tokens": 4096,
                    "history_len": 10,
                    "prompt_name": "default",
                    "callbacks": True,
                },
            },
            "action_model": {
                self.DEFAULT_LLM_MODEL: {
                    "temperature": 0.01,
                    "max_tokens": 4096,
                    "prompt_name": "ChatGLM3",
                    "callbacks": True,
                },
            },
            "postprocess_model": {
                self.DEFAULT_LLM_MODEL: {
                    "temperature": 0.01,
                    "max_tokens": 4096,
                    "prompt_name": "default",
                    "callbacks": True,
                }
            },
            "image_model": {
                "sd-turbo": {
                    "size": "256*256",
                }
            },
        }

    def default_llm_model(self, llm_model: str):
        self.DEFAULT_LLM_MODEL = llm_model

    def default_embedding_model(self, embedding_model: str):
        self.DEFAULT_EMBEDDING_MODEL = embedding_model

    def agent_model(self, agent_model: str):
        self.Agent_MODEL = agent_model

    def history_len(self, history_len: int):
        self.HISTORY_LEN = history_len

    def max_tokens(self, max_tokens: int):
        self.MAX_TOKENS = max_tokens

    def temperature(self, temperature: float):
        self.TEMPERATURE = temperature

    def support_agent_models(self, support_agent_models: List[str]):
        self.SUPPORT_AGENT_MODELS = support_agent_models

    def model_platforms(self, model_platforms: List[Dict[str, Any]]):
        self.MODEL_PLATFORMS = model_platforms

    def tool_config(self, tool_config: Dict[str, Any]):
        self.TOOL_CONFIG = tool_config

    def get_config(self) -> ConfigModel:
        config = ConfigModel()
        config.DEFAULT_LLM_MODEL = self.DEFAULT_LLM_MODEL
        config.DEFAULT_EMBEDDING_MODEL = self.DEFAULT_EMBEDDING_MODEL
        config.Agent_MODEL = self.Agent_MODEL
        config.HISTORY_LEN = self.HISTORY_LEN
        config.MAX_TOKENS = self.MAX_TOKENS
        config.TEMPERATURE = self.TEMPERATURE
        config.SUPPORT_AGENT_MODELS = self.SUPPORT_AGENT_MODELS
        config.LLM_MODEL_CONFIG = self.LLM_MODEL_CONFIG
        config.MODEL_PLATFORMS = self.MODEL_PLATFORMS
        config.TOOL_CONFIG = self.TOOL_CONFIG

        return config


class ConfigModelWorkSpace(
    core_config.ConfigWorkSpace[ConfigModelFactory, ConfigModel]
):
    """
    工作空间的配置预设, 提供ConfigModel建造方法产生实例。
    """

    config_factory_cls = ConfigModelFactory

    def __init__(self):
        super().__init__()

    def _build_config_factory(self, config_json: Any) -> ConfigModelFactory:
        _config_factory = self.config_factory_cls()
        if config_json.get("DEFAULT_LLM_MODEL"):
            _config_factory.default_llm_model(config_json.get("DEFAULT_LLM_MODEL"))
        if config_json.get("DEFAULT_EMBEDDING_MODEL"):
            _config_factory.default_embedding_model(
                config_json.get("DEFAULT_EMBEDDING_MODEL")
            )
        if config_json.get("Agent_MODEL"):
            _config_factory.agent_model(config_json.get("Agent_MODEL"))
        if config_json.get("HISTORY_LEN"):
            _config_factory.history_len(config_json.get("HISTORY_LEN"))
        if config_json.get("MAX_TOKENS"):
            _config_factory.max_tokens(config_json.get("MAX_TOKENS"))
        if config_json.get("TEMPERATURE"):
            _config_factory.temperature(config_json.get("TEMPERATURE"))
        if config_json.get("SUPPORT_AGENT_MODELS"):
            _config_factory.support_agent_models(
                config_json.get("SUPPORT_AGENT_MODELS")
            )
        if config_json.get("MODEL_PLATFORMS"):
            _config_factory.model_platforms(config_json.get("MODEL_PLATFORMS"))
        if config_json.get("TOOL_CONFIG"):
            _config_factory.tool_config(config_json.get("TOOL_CONFIG"))

        return _config_factory

    @classmethod
    def get_type(cls) -> str:
        return ConfigModel.class_name()

    def get_config(self) -> ConfigModel:
        return self._config_factory.get_config()

    def set_default_llm_model(self, llm_model: str):
        self._config_factory.default_llm_model(llm_model)
        self.store_config()

    def set_default_embedding_model(self, embedding_model: str):
        self._config_factory.default_embedding_model(embedding_model)
        self.store_config()

    def set_agent_model(self, agent_model: str):
        self._config_factory.agent_model(agent_model)
        self.store_config()

    def set_history_len(self, history_len: int):
        self._config_factory.history_len(history_len)
        self.store_config()

    def set_max_tokens(self, max_tokens: int):
        self._config_factory.max_tokens(max_tokens)
        self.store_config()

    def set_temperature(self, temperature: float):
        self._config_factory.temperature(temperature)
        self.store_config()

    def set_support_agent_models(self, support_agent_models: List[str]):
        self._config_factory.support_agent_models(support_agent_models)
        self.store_config()

    def set_model_platforms(self, model_platforms: List[Dict[str, Any]]):
        self._config_factory.model_platforms(model_platforms=model_platforms)
        self.store_config()

    def set_tool_config(self, tool_config: Dict[str, Any]):
        self._config_factory.tool_config(tool_config=tool_config)
        self.store_config()


config_model_workspace: ConfigModelWorkSpace = ConfigModelWorkSpace()

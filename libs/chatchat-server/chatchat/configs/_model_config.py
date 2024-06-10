import os

# 默认选用的 LLM 名称
DEFAULT_LLM_MODEL = "chatglm3-6b"

# 默认选用的 Embedding 名称
DEFAULT_EMBEDDING_MODEL = "bge-large-zh-v1.5"


# AgentLM模型的名称 (可以不指定，指定之后就锁定进入Agent之后的Chain的模型，不指定就是LLM_MODELS[0])
Agent_MODEL = None

# 历史对话轮数
HISTORY_LEN = 3

# 大模型最长支持的长度，如果不填写，则使用模型默认的最大长度，如果填写，则为用户设定的最大长度
MAX_TOKENS = None

# LLM通用对话参数
TEMPERATURE = 0.7
# TOP_P = 0.95 # ChatOpenAI暂不支持该参数

SUPPORT_AGENT_MODELS = [
    "chatglm3-6b",
    "openai-api",
    "Qwen-14B-Chat",
    "Qwen-7B-Chat",
    "qwen-turbo",
]


LLM_MODEL_CONFIG = {
    # 意图识别不需要输出，模型后台知道就行
    "preprocess_model": {
        DEFAULT_LLM_MODEL: {
            "temperature": 0.05,
            "max_tokens": 4096,
            "history_len": 100,
            "prompt_name": "default",
            "callbacks": False
        },
    },
    "llm_model": {
        DEFAULT_LLM_MODEL: {
            "temperature": 0.9,
            "max_tokens": 4096,
            "history_len": 10,
            "prompt_name": "default",
            "callbacks": True
        },
    },
    "action_model": {
        DEFAULT_LLM_MODEL: {
            "temperature": 0.01,
            "max_tokens": 4096,
            "prompt_name": "ChatGLM3",
            "callbacks": True
        },
    },
    "postprocess_model": {
        DEFAULT_LLM_MODEL: {
            "temperature": 0.01,
            "max_tokens": 4096,
            "prompt_name": "default",
            "callbacks": True
        }
    },
    "image_model": {
        "sd-turbo": {
            "size": "256*256",
        }
    }
}

# 可以通过 model_providers 提供转换不同平台的接口为openai endpoint的能力，启动后下面变量会自动增加相应的平台
#   ### 如果您已经有了一个openai endpoint的能力的地址，可以在这里直接配置
#   - platform_name 可以任意填写，不要重复即可
#   - platform_type 以后可能根据平台类型做一些功能区分,与platform_name一致即可
#   - 将框架部署的模型填写到对应列表即可。不同框架可以加载同名模型，项目会自动做负载均衡。


# 创建一个全局的共享字典
MODEL_PLATFORMS = [

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
        "api_key": "EMPTY",
        "api_concurrencies": 5,
        "llm_models": [
            "glm-4",
            "qwen2-instruct",
            "qwen1.5-chat",
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

MODEL_PROVIDERS_CFG_PATH_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_providers.yaml")
MODEL_PROVIDERS_CFG_HOST = "127.0.0.1"

MODEL_PROVIDERS_CFG_PORT = 20000
# 工具配置项
TOOL_CONFIG = {
    "search_local_knowledgebase": {
        "use": False,
        "top_k": 3,
        "score_threshold": 1.0,
        "conclude_prompt": {
            "with_result":
                '<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 "根据已知信息无法回答该问题"，'
                '不允许在答案中添加编造成分，答案请使用中文。 </指令>\n'
                '<已知信息>{{ context }}</已知信息>\n'
                '<问题>{{ question }}</问题>\n',
            "without_result":
                '请你根据我的提问回答我的问题:\n'
                '{{ question }}\n'
                '请注意，你必须在回答结束后强调，你的回答是根据你的经验回答而不是参考资料回答的。\n',
        }
    },
    "search_internet": {
        "use": False,
        "search_engine_name": "bing",
        "search_engine_config":
            {
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
                "duckduckgo": {
                    "result_len": 3
                }
            },
        "top_k": 10,
        "verbose": "Origin",
        "conclude_prompt":
            "<指令>这是搜索到的互联网信息，请你根据这些信息进行提取并有调理，简洁的回答问题。如果无法从中得到答案，请说 “无法搜索到能回答问题的内容”。 "
            "</指令>\n<已知信息>{{ context }}</已知信息>\n"
            "<问题>\n"
            "{{ question }}\n"
            "</问题>\n"
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
        "device": "cuda:1"
    },
    "aqa_processor": {
        "use": False,
        "model_path": "your model path",
        "tokenizer_path": "yout tokenizer path",
        "device": "cuda:2"
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
        #限定返回的行数
        "top_k":50,
        #是否返回中间步骤
        "return_intermediate_steps": True,
        #如果想指定特定表，请填写表名称，如["sys_user","sys_dept"]，不填写走智能判断应该使用哪些表
        "table_names":[],
        #对表名进行额外说明，辅助大模型更好的判断应该使用哪些表，尤其是SQLDatabaseSequentialChain模式下,是根据表名做的预测，很容易误判。
        "table_comments":{
            # 如果出现大模型选错表的情况，可尝试根据实际情况填写表名和说明
            # "tableA":"这是一个用户表，存储了用户的基本信息",
            # "tanleB":"角色表",
        }
    },
}

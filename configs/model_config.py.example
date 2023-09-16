import os
import logging
# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)
# 是否显示详细日志
log_verbose = False


# 在以下字典中修改属性值，以指定本地embedding模型存储位置
# 如将 "text2vec": "GanymedeNil/text2vec-large-chinese" 修改为 "text2vec": "User/Downloads/text2vec-large-chinese"
# 此处请写绝对路径
embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec-base": "shibing624/text2vec-base-chinese",
    "text2vec": "GanymedeNil/text2vec-large-chinese",
    "text2vec-paraphrase": "shibing624/text2vec-base-chinese-paraphrase",
    "text2vec-sentence": "shibing624/text2vec-base-chinese-sentence",
    "text2vec-multilingual": "shibing624/text2vec-base-multilingual",
    "text2vec-bge-large-chinese": "shibing624/text2vec-bge-large-chinese",
    "m3e-small": "moka-ai/m3e-small",
    "m3e-base": "moka-ai/m3e-base",
    "m3e-large": "moka-ai/m3e-large",
    "bge-small-zh": "BAAI/bge-small-zh",
    "bge-base-zh": "BAAI/bge-base-zh",
    "bge-large-zh": "BAAI/bge-large-zh",
    "bge-large-zh-noinstruct": "BAAI/bge-large-zh-noinstruct",
    "piccolo-base-zh": "sensenova/piccolo-base-zh",
    "piccolo-large-zh": "sensenova/piccolo-large-zh",
    "text-embedding-ada-002": os.environ.get("OPENAI_API_KEY")
}

# 选用的 Embedding 名称
EMBEDDING_MODEL = "m3e-base"

# Embedding 模型运行设备。设为"auto"会自动检测，也可手动设定为"cuda","mps","cpu"其中之一。
EMBEDDING_DEVICE = "auto"

llm_model_dict = {
    "chatglm-6b": {
        "local_model_path": "THUDM/chatglm-6b",
        "api_base_url": "http://localhost:8888/v1",  # "name"修改为fastchat服务中的"api_base_url"
        "api_key": "EMPTY"
    },

    "chatglm2-6b": {
        "local_model_path": "THUDM/chatglm2-6b",
        "api_base_url": "http://localhost:8888/v1",  # URL需要与运行fastchat服务端的server_config.FSCHAT_OPENAI_API一致
        "api_key": "EMPTY"
    },

    "chatglm2-6b-32k": {
        "local_model_path": "THUDM/chatglm2-6b-32k",  # "THUDM/chatglm2-6b-32k",
        "api_base_url": "http://localhost:8888/v1",  # "URL需要与运行fastchat服务端的server_config.FSCHAT_OPENAI_API一致
        "api_key": "EMPTY"
    },

    # 调用chatgpt时如果报出： urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='api.openai.com', port=443):
    #  Max retries exceeded with url: /v1/chat/completions
    # 则需要将urllib3版本修改为1.25.11
    # 如果依然报urllib3.exceptions.MaxRetryError: HTTPSConnectionPool，则将https改为http
    # 参考https://zhuanlan.zhihu.com/p/350015032

    # 如果报出：raise NewConnectionError(
    # urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPSConnection object at 0x000001FE4BDB85E0>:
    # Failed to establish a new connection: [WinError 10060]
    # 则是因为内地和香港的IP都被OPENAI封了，需要切换为日本、新加坡等地

    # 如果出现WARNING: Retrying langchain.chat_models.openai.acompletion_with_retry.<locals>._completion_with_retry in
    # 4.0 seconds as it raised APIConnectionError: Error communicating with OpenAI.
    # 需要添加代理访问(正常开的代理软件可能会拦截不上)需要设置配置openai_proxy 或者 使用环境遍历OPENAI_PROXY 进行设置
    # 比如: "openai_proxy": 'http://127.0.0.1:4780'
    "gpt-3.5-turbo": {
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "",
        "openai_proxy": ""
    },
    # 线上模型。当前支持智谱AI。
    # 如果没有设置有效的local_model_path，则认为是在线模型API。
    # 请在server_config中为每个在线API设置不同的端口
    # 具体注册及api key获取请前往 http://open.bigmodel.cn
    "zhipu-api": {
        "api_base_url": "http://127.0.0.1:8888/v1",
        "api_key": "",
        "provider": "ChatGLMWorker",
        "version": "chatglm_pro",  # 可选包括 "chatglm_lite", "chatglm_std", "chatglm_pro"
    },
    "minimax-api": {
        "api_base_url": "http://127.0.0.1:8888/v1",
        "group_id": "",
        "api_key": "",
        "is_pro": False,
        "provider": "MiniMaxWorker",
    },
    "xinghuo-api": {
        "api_base_url": "http://127.0.0.1:8888/v1",
        "APPID": "",
        "APISecret": "",
        "api_key": "",
        "is_v2": False,
        "provider": "XingHuoWorker",
    },
    # 百度千帆 API，申请方式请参考 https://cloud.baidu.com/doc/WENXINWORKSHOP/s/4lilb2lpf
    "qianfan-api": {
        "version": "ernie-bot",  # 当前支持 "ernie-bot" 或 "ernie-bot-turbo"， 更多的见文档模型支持列表中千帆部分。
        "version_url": "", # 可以不填写version，直接填写在千帆申请模型发布的API地址
        "api_base_url": "http://127.0.0.1:8888/v1",
        "api_key": "",
        "secret_key": "",
        "provider": "QianFanWorker",
    }
}

# LLM 名称
LLM_MODEL = "chatglm2-6b"

# 历史对话轮数
HISTORY_LEN = 3

# LLM通用对话参数
TEMPERATURE = 0.7
# TOP_P = 0.95 # ChatOpenAI暂不支持该参数


# LLM 运行设备。设为"auto"会自动检测，也可手动设定为"cuda","mps","cpu"其中之一。
LLM_DEVICE = "auto"

# TextSplitter

text_splitter_dict = {
    "ChineseRecursiveTextSplitter": {
        "source": "",
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
        "headers_to_split_on":
            [
                ("#", "head1"),
                ("##", "head2"),
                ("###", "head3"),
                ("####", "head4"),
            ]
    },
}

# TEXT_SPLITTER 名称
TEXT_SPLITTER = "ChineseRecursiveTextSplitter"

# 知识库中单段文本长度(不适用MarkdownHeaderTextSplitter)
CHUNK_SIZE = 250

# 知识库中相邻文本重合长度(不适用MarkdownHeaderTextSplitter)
OVERLAP_SIZE = 0


# 日志存储路径
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# 知识库默认存储路径
KB_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
if not os.path.exists(KB_ROOT_PATH):
    os.mkdir(KB_ROOT_PATH)
# 数据库默认存储路径。
# 如果使用sqlite，可以直接修改DB_ROOT_PATH；如果使用其它数据库，请直接修改SQLALCHEMY_DATABASE_URI。
DB_ROOT_PATH = os.path.join(KB_ROOT_PATH, "info.db")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_ROOT_PATH}"


# 可选向量库类型及对应配置
kbs_config = {
    "faiss": {
    },
    "milvus": {
        "host": "127.0.0.1",
        "port": "19530",
        "user": "",
        "password": "",
        "secure": False,
    },
    "pg": {
        "connection_uri": "postgresql://postgres:postgres@127.0.0.1:5432/langchain_chatchat",
    }
}

# 默认向量库类型。可选：faiss, milvus, pg.
DEFAULT_VS_TYPE = "faiss"

# 缓存向量库数量
CACHED_VS_NUM = 1

# 知识库匹配向量数量
VECTOR_SEARCH_TOP_K = 3

# 知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右
SCORE_THRESHOLD = 1

# 搜索引擎匹配结题数量
SEARCH_ENGINE_TOP_K = 3

# nltk 模型存储路径
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")

# 基于本地知识问答的提示词模版（使用Jinja2语法，简单点就是用双大括号代替f-string的单大括号
PROMPT_TEMPLATE = """<指令>根据已知信息，简洁和专业的来回答问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分，答案请使用中文。 </指令>

<已知信息>{{ context }}</已知信息>

<问题>{{ question }}</问题>"""

# API 是否开启跨域，默认为False，如果需要开启，请设置为True
# is open cross domain
OPEN_CROSS_DOMAIN = False

# Bing 搜索必备变量
# 使用 Bing 搜索需要使用 Bing Subscription Key,需要在azure port中申请试用bing search
# 具体申请方式请见
# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/create-bing-search-service-resource
# 使用python创建bing api 搜索实例详见:
# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/quickstarts/rest/python
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
# 注意不是bing Webmaster Tools的api key，

# 此外，如果是在服务器上，报Failed to establish a new connection: [Errno 110] Connection timed out
# 是因为服务器加了防火墙，需要联系管理员加白名单，如果公司的服务器的话，就别想了GG
BING_SUBSCRIPTION_KEY = ""

# 是否开启中文标题加强，以及标题增强的相关配置
# 通过增加标题判断，判断哪些文本为标题，并在metadata中进行标记；
# 然后将文本与往上一级的标题进行拼合，实现文本信息的增强。
ZH_TITLE_ENHANCE = False

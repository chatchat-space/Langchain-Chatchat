![](docs/img/logo-long-chatchat-trans-v2.png)

🌍 [READ THIS IN ENGLISH](README_en.md)

📃 **LangChain-Chatchat** (原 Langchain-ChatGLM)

基于 ChatGLM 等大语言模型与 Langchain 等应用框架实现，开源、可离线部署的 RAG 与 Agent 应用项目。

---

## 目录

* [概述](README.md#概述)
* [功能介绍](README.md#Langchain-Chatchat-提供哪些功能)
* [快速上手](README.md#快速上手)
    * [安装部署](README.md#安装部署)
* [项目里程碑](README.md#项目里程碑)
* [联系我们](README.md#联系我们)

## 概述

🤖️ 一种利用 [langchain](https://github.com/langchain-ai/langchain)
思想实现的基于本地知识库的问答应用，目标期望建立一套对中文场景与开源模型支持友好、可离线运行的知识库问答解决方案。

💡 受 [GanymedeNil](https://github.com/GanymedeNil) 的项目 [document.ai](https://github.com/GanymedeNil/document.ai)
和 [AlexZhangji](https://github.com/AlexZhangji)
创建的 [ChatGLM-6B Pull Request](https://github.com/THUDM/ChatGLM-6B/pull/216)
启发，建立了全流程可使用开源模型实现的本地知识库问答应用。本项目的最新版本中可使用 [Xinference](https://github.com/xorbitsai/inference)、[Ollama](https://github.com/ollama/ollama)
等框架接入 [GLM-4-Chat](https://github.com/THUDM/GLM-4)、 [Qwen2-Instruct](https://github.com/QwenLM/Qwen2)、 [Llama3](https://github.com/meta-llama/llama3)
等模型，依托于 [langchain](https://github.com/langchain-ai/langchain)
框架支持通过基于 [FastAPI](https://github.com/tiangolo/fastapi) 提供的 API
调用服务，或使用基于 [Streamlit](https://github.com/streamlit/streamlit) 的 WebUI 进行操作。

![](docs/img/langchain_chatchat_0.3.0.png)

✅ 本项目支持市面上主流的开源 LLM、 Embedding 模型与向量数据库，可实现全部使用**开源**模型**离线私有部署**。与此同时，本项目也支持
OpenAI GPT API 的调用，并将在后续持续扩充对各类模型及模型 API 的接入。

⛓️ 本项目实现原理如下图所示，过程包括加载文件 -> 读取文本 -> 文本分割 -> 文本向量化 -> 问句向量化 ->
在文本向量中匹配出与问句向量最相似的 `top k`个 -> 匹配出的文本作为上下文和问题一起添加到 `prompt`中 -> 提交给 `LLM`生成回答。

📺 [原理介绍视频](https://www.bilibili.com/video/BV13M4y1e7cN/?share_source=copy_web&vd_source=e6c5aafe684f30fbe41925d61ca6d514)

![实现原理图](docs/img/langchain+chatglm.png)

从文档处理角度来看，实现流程如下：

![实现原理图2](docs/img/langchain+chatglm2.png)

🚩 本项目未涉及微调、训练过程，但可利用微调或训练对本项目效果进行优化。

🌐 [AutoDL 镜像](https://www.codewithgpu.com/i/chatchat-space/Langchain-Chatchat/Langchain-Chatchat) 中 `0.3.0`
版本所使用代码已更新至本项目 `v0.3.0` 版本。

🐳 Docker 镜像将会在近期更新。

🧑‍💻 如果你想对本项目做出贡献，欢迎移步[开发指南](docs/contributing/README_dev.md) 获取更多开发部署相关信息。

## Langchain-Chatchat 提供哪些功能

### 0.3.x 版本功能一览

| 功能        | 0.2.x                            | 0.3.x                                                               |
|-----------|----------------------------------|---------------------------------------------------------------------|
| 模型接入      | 本地：fastchat<br>在线：XXXModelWorker | 本地：model_provider,支持大部分主流模型加载框架<br>在线：oneapi<br>所有模型接入均兼容openai sdk |
| Agent     | ❌不稳定                             | ✅针对ChatGLM3和QWen进行优化,Agent能力显著提升                                    ||
| LLM对话     | ✅                                | ✅                                                                   ||
| 知识库对话     | ✅                                | ✅                                                                   ||
| 搜索引擎对话    | ✅                                | ✅                                                                   ||
| 文件对话      | ✅仅向量检索                           | ✅统一为File RAG功能,支持BM25+KNN等多种检索方式                                    ||
| 数据库对话     | ❌                                | ✅                                                                   ||
| ARXIV文献对话 | ❌                                | ✅                                                                   ||
| Wolfram对话 | ❌                                | ✅                                                                   ||
| 文生图       | ❌                                | ✅                                                                   ||
| 本地知识库管理   | ✅                                | ✅                                                                   ||
| WEBUI     | ✅                                | ✅更好的多会话支持,自定义系统提示词...                                               |

0.3.x 版本的核心功能由 Agent 实现,但用户也可以手动实现工具调用:

|操作方式|实现的功能|适用场景|
|-------|---------|-------|
|选中"启用Agent",选择多个工具|由LLM自动进行工具调用|使用ChatGLM3/Qwen或在线API等具备Agent能力的模型|
|选中"启用Agent",选择单个工具|LLM仅解析工具参数|使用的模型Agent能力一般,不能很好的选择工具<br>想手动选择功能|
|不选中"启用Agent",选择单个工具|不使用Agent功能的情况下,手动填入参数进行工具调用|使用的模型不具备Agent能力|

更多功能和更新请实际部署体验.

### 已支持的模型部署框架与模型

本项目中已经支持市面上主流的如 [GLM-4-Chat](https://github.com/THUDM/GLM-4)
与 [Qwen2-Instruct](https://github.com/QwenLM/Qwen2) 等新近开源大语言模型和 Embedding
模型，这些模型需要用户自行启动模型部署框架后，通过修改配置信息接入项目，本项目已支持的本地模型部署框架如下：

| 模型部署框架             | Xinference                                                                               | LocalAI                                                    | Ollama                                                                         | FastChat                                                                             |
|--------------------|------------------------------------------------------------------------------------------|------------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| OpenAI API 接口对齐    | ✅                                                                                        | ✅                                                          | ✅                                                                              | ✅                                                                                    |
| 加速推理引擎             | GPTQ, GGML, vLLM, TensorRT                                                               | GPTQ, GGML, vLLM, TensorRT                                 | GGUF, GGML                                                                     | vLLM                                                                                 |
| 接入模型类型             | LLM, Embedding, Rerank, Text-to-Image, Vision, Audio                                     | LLM, Embedding, Rerank, Text-to-Image, Vision, Audio       | LLM, Text-to-Image, Vision                                                     | LLM, Vision                                                                          |
| Function Call      | ✅                                                                                        | ✅                                                          | ✅                                                                              | /                                                                                    |
| 更多平台支持(CPU, Metal) | ✅                                                                                        | ✅                                                          | ✅                                                                              | ✅                                                                                    |
| 异构                 | ✅                                                                                        | ✅                                                          | /                                                                              | /                                                                                    |
| 集群                 | ✅                                                                                        | ✅                                                          | /                                                                              | /                                                                                    |
| 操作文档链接             | [Xinference 文档](https://inference.readthedocs.io/zh-cn/latest/models/builtin/index.html) | [LocalAI 文档](https://localai.io/model-compatibility/)      | [Ollama 文档](https://github.com/ollama/ollama?tab=readme-ov-file#model-library) | [FastChat 文档](https://github.com/lm-sys/FastChat#install)                            |
| 可用模型               | [Xinference 已支持模型](https://inference.readthedocs.io/en/latest/models/builtin/index.html) | [LocalAI 已支持模型](https://localai.io/model-compatibility/#/) | [Ollama 已支持模型](https://ollama.com/library#/)                                   | [FastChat 已支持模型](https://github.com/lm-sys/FastChat/blob/main/docs/model_support.md) |

除上述本地模型加载框架外，项目中也为可接入在线 API 的 [One API](https://github.com/songquanpeng/one-api)
框架接入提供了支持，支持包括 [OpenAI ChatGPT](https://platform.openai.com/docs/guides/gpt/chat-completions-api)、[Azure OpenAI API](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)、[Anthropic Claude](https://anthropic.com/)、[智谱请言](https://bigmodel.cn/)、[百川](https://platform.baichuan-ai.com/)
等常用在线 API 的接入使用。

> [!Note]
> 关于 Xinference 加载本地模型:
> Xinference 内置模型会自动下载,如果想让它加载本机下载好的模型,可以在启动 Xinference 服务后,到项目 tools/model_loaders
> 目录下执行 `streamlit run xinference_manager.py`,按照页面提示为指定模型设置本地路径即可.

## 快速上手

### 安装部署

#### 0. 软硬件要求

💡 软件方面，本项目已支持在 Python 3.8-3.11 环境中进行使用，并已在 Windows、macOS、Linux 操作系统中进行测试。

💻 硬件方面，因 0.3.0 版本已修改为支持不同模型部署框架接入，因此可在 CPU、GPU、NPU、MPS 等不同硬件条件下使用。

#### 1. 安装 Langchain-Chatchat

从 0.3.0 版本起，Langchain-Chatchat 提供以 Python 库形式的安装方式，具体安装请执行：

```shell
pip install langchain-chatchat -U
```

> [!important]
> 为确保所使用的 Python 库为最新版，建议使用官方 Pypi 源或清华源。

> [!Note]
> 因模型部署框架 Xinference 接入 Langchain-Chatchat 时需要额外安装对应的 Python 依赖库，因此如需搭配 Xinference
> 框架使用时，建议使用如下安装方式：
> ```shell
> pip install langchain-chatchat[xinference] -U
> ```

#### 2. 模型推理框架并加载模型

从 0.3.0 版本起，Langchain-Chatchat 不再根据用户输入的本地模型路径直接进行模型加载，涉及到的模型种类包括
LLM、Embedding、Reranker
及后续会提供支持的多模态模型等，均改为支持市面常见的各大模型推理框架接入，如 [Xinference](https://github.com/xorbitsai/inference)、[Ollama](https://github.com/ollama/ollama)、[LocalAI](https://github.com/mudler/LocalAI)、[FastChat](https://github.com/lm-sys/FastChat)、[One API](https://github.com/songquanpeng/one-api)
等。

因此，请确认在启动 Langchain-Chatchat 项目前，首先进行模型推理框架的运行，并加载所需使用的模型。

这里以 Xinference 举例,
请参考 [Xinference文档](https://inference.readthedocs.io/zh-cn/latest/getting_started/installation.html) 进行框架部署与模型加载。

> [!WARNING]  
> 为避免依赖冲突，请将 Langchain-Chatchat 和模型部署框架如 Xinference 等放在不同的 Python 虚拟环境中, 比如 conda, venv,
> virtualenv 等。

#### 3. 查看与修改 Langchain-Chatchat 配置

从 0.3.0 版本起，Langchain-Chatchat 不再使用本地文件的方式进行配置修改，改为使用命令行的方式，并会在后续版本中增加配置项修改页面。

以下从查看配置、修改配置两种操作类型进行介绍。

##### 3.1 查看 chatchat-config 命令帮助

输入以下命令查看可选配置类型：

```shell
chatchat-config --help
```

这时会得到返回：

```text 
Usage: chatchat-config [OPTIONS] COMMAND [ARGS]...

  指令` chatchat-config` 工作空间配置

Options:
  --help  Show this message and exit.

Commands:
  basic   基础配置
  kb      知识库配置
  model   模型配置
  server  服务配置
```

可根据上述配置命令选择需要查看或修改的配置类型，以`基础配置`为例，想要进行`基础配置`查看或修改时可以输入以下命令获取帮助信息：

```shell
chatchat-config basic --help
```

这时会得到返回信息：

```text
Usage: chatchat-config basic [OPTIONS]

  基础配置

Options:
  --verbose [true|false]  是否开启详细日志
  --data TEXT             初始化数据存放路径，注意：目录会清空重建
  --format TEXT           日志格式
  --clear                 清除配置
  --show                  显示配置
  --help                  Show this message and exit.
```

##### 3.2 使用 chatchat-config 查看对应配置参数

以`基础配置`为例，可根据上述命令帮助内容确认，需要查看`基础配置`的配置参数，可直接输入：

```shell
chatchat-config basic --show
```

在未进行配置项修改时，可得到默认配置内容如下：

```text 
{
    "log_verbose": false,
    "CHATCHAT_ROOT": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat",
    "DATA_PATH": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data",
    "IMG_DIR": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/img",
    "NLTK_DATA_PATH": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data/nltk_data",
    "LOG_FORMAT": "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    "LOG_PATH": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data/logs",
    "MEDIA_PATH": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data/media",
    "BASE_TEMP_DIR": "/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data/temp",
    "class_name": "ConfigBasic"
}
```

##### 3.3 使用 chatchat-config 修改对应配置参数

以修改`模型配置`中`默认llm模型`为例，可以执行以下命令行查看配置项名称：

```shell
chatchat-config model --help
```

这时会得到

```text 
Usage: chatchat-config model [OPTIONS]

  模型配置

Options:
  --default_llm_model TEXT        默认llm模型
  --default_embedding_model TEXT  默认embedding模型
  --agent_model TEXT              agent模型
  --history_len INTEGER           历史长度
  --max_tokens INTEGER            最大tokens
  --temperature FLOAT             温度
  --support_agent_models TEXT     支持的agent模型
  --model_providers_cfg_path_config TEXT
                                  模型平台配置文件路径
  --model_providers_cfg_host TEXT
                                  模型平台配置服务host
  --model_providers_cfg_port INTEGER
                                  模型平台配置服务port
  --set_model_platforms TEXT      模型平台配置 as a JSON string.
  --set_tool_config TEXT          工具配置项  as a JSON string.
  --clear                         清除配置
  --show                          显示配置
  --help                          Show this message and exit.
```

可首先查看当前`模型配置`的配置项：

```shell
chatchat-config model --show
```

这时会得到:

```text 
{
    "DEFAULT_LLM_MODEL": "glm4-chat",
    "DEFAULT_EMBEDDING_MODEL": "bge-large-zh-v1.5",
    "Agent_MODEL": null,
    "HISTORY_LEN": 3,
    "MAX_TOKENS": null,
    "TEMPERATURE": 0.7,
    ...
    "class_name": "ConfigModel"
}
```

需要修改`默认llm模型`为`qwen2-instruct`时，可执行：

```shell
chatchat-config model --default_llm_model qwen2-instruct
```

更多配置项修改帮助请参考 [README.md](libs/chatchat-server/README.md)

#### 4. 自定义模型接入配置

完成上述项目配置项查看与修改后，需要根据步骤**2. 模型推理框架并加载模型**
中选用的模型推理框架与加载的模型进行模型接入配置，其中模型推理框架包括 [Xinference](https://github.com/xorbitsai/inference)、[Ollama](https://github.com/ollama/ollama)、[LocalAI](https://github.com/mudler/LocalAI)、[FastChat](https://github.com/lm-sys/FastChat)、[One API](https://github.com/songquanpeng/one-api)
等，可以提供 [GLM-4-Chat](https://github.com/THUDM/GLM-4) 与 [Qwen2-Instruct](https://github.com/QwenLM/Qwen2)
等中文最新开源模型的接入支持。

参考配置 3.2 中 `CHATCHAT_ROOT` 变量指向的路径下 configs 中的 `model_providers.yaml` 文件, 即可完成自定义平台加载.

```shell
# 这里应为 3.2 中 "CHATCHAT_ROOT" 变量指向目录
cd /root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat
vim model_providers.yaml
```

配置介绍请参考 [model-providers/README.md](libs/model-providers/README.md)

详细配置请参考 [model_providers.yaml](libs/model-providers/model_providers.yaml)

#### 5. 初始化知识库

> [!WARNING]  
> 进行知识库初始化前，请确保已经启动模型推理框架及对应 `embedding` 模型，且已按照上述**步骤3**与**步骤4**完成模型接入配置。

```shell
cd # 回到原始目录
chatchat-kb -r
```

指定 text-embedding 模型进行初始化(如有需要):

```shell
cd # 回到原始目录
chatchat-kb -r --embed-model=text-embedding-3-small
```

出现以下日志即为成功:

```text 

----------------------------------------------------------------------------------------------------
知识库名称      ：samples
知识库类型      ：faiss
向量模型：      ：bge-large-zh-v1.5
知识库路径      ：/root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data/knowledge_base/samples
文件总数量      ：47
入库文件数      ：42
知识条目数      ：740
用时            ：0:02:29.701002
----------------------------------------------------------------------------------------------------

总计用时        ：0:02:33.414425

2024-06-17 22:30:47,933 - init_database.py[line:176] - WARNING: Sending SIGKILL to <Process name='Model providers Server (3949160)' pid=3949160 parent=3949098 started daemon>
```

知识库路径为 3.2 中 *DATA_PATH* 变量指向的路径下的 knowledge_base 目录中:

```shell
(chatchat) [root@VM-centos ~]# ls /root/anaconda3/envs/chatchat/lib/python3.11/site-packages/chatchat/data/knowledge_base/samples/vector_store
bge-large-zh-v1.5  text-embedding-3-small
```

#### 6. 启动项目

```shell
chatchat -a
```

出现以下界面即为启动成功:

![WebUI界面](docs/img/langchain_chatchat_webui.png)

> [!WARNING]  
> 由于 chatchat-config server 配置默认监听地址 `DEFAULT_BIND_HOST` 为 127.0.0.1, 所以无法通过其他 ip 进行访问。
>
> 如需修改请参考以下方式：
> <details>
> ```shell
> chatchat-config server --show
> ```
>
> 这时会得到
> ```text 
> {
>     "HTTPX_DEFAULT_TIMEOUT": 300.0,
>     "OPEN_CROSS_DOMAIN": true,
>     "DEFAULT_BIND_HOST": "127.0.0.1",
>     "WEBUI_SERVER_PORT": 8501,
>     "API_SERVER_PORT": 7861,
>     "WEBUI_SERVER": {
>         "host": "127.0.0.1",
>         "port": 8501
>     },
>     "API_SERVER": {
>         "host": "127.0.0.1",
>         "port": 7861
>     },
>     "class_name": "ConfigServer"
> }
> ```
>
> 如需通过机器ip 进行访问(如 Linux 系统), 需要将监听地址修改为 0.0.0.0。
> ```shell
> chatchat-config server --default_bind_host=0.0.0.0
> ```
>
> 这时会得到
> ```text 
> {
>     "HTTPX_DEFAULT_TIMEOUT": 300.0,
>     "OPEN_CROSS_DOMAIN": true,
>     "DEFAULT_BIND_HOST": "0.0.0.0",
>     "WEBUI_SERVER_PORT": 8501,
>     "API_SERVER_PORT": 7861,
>     "WEBUI_SERVER": {
>         "host": "0.0.0.0",
>         "port": 8501
>     },
>     "API_SERVER": {
>         "host": "0.0.0.0",
>         "port": 7861
>     },
>     "class_name": "ConfigServer"
> }
> ```
> </details>

### 旧版本迁移

* 0.3.x 结构改变很大,强烈建议您按照文档重新部署. 以下指南不保证100%兼容和成功. 记得提前备份重要数据!

- 首先按照 `安装部署` 中的步骤配置运行环境
- 配置 `DATA` 等选项
- 将 0.2.x 项目的 knowledge_base 目录拷贝到配置的 `DATA` 目录下

---

## 项目里程碑

+ `2023年4月`: `Langchain-ChatGLM 0.1.0` 发布，支持基于 ChatGLM-6B 模型的本地知识库问答。
+ `2023年8月`: `Langchain-ChatGLM` 改名为 `Langchain-Chatchat`，发布 `0.2.0` 版本，使用 `fastchat` 作为模型加载方案，支持更多的模型和数据库。
+ `2023年10月`: `Langchain-Chatchat 0.2.5` 发布，推出 Agent 内容，开源项目在`Founder Park & Zhipu AI & Zilliz`
  举办的黑客马拉松获得三等奖。
+ `2023年12月`: `Langchain-Chatchat` 开源项目获得超过 **20K** stars.
+ `2024年6月`: `Langchain-Chatchat 0.3.0` 发布，带来全新项目架构。

+ 🔥 让我们一起期待未来 Chatchat 的故事 ···

---

## 协议

本项目非涉及 额外协议 部分的代码遵循 [Apache-2.0](LICENSE) 协议。

### 额外协议

本仓库中的 [model-providers 代码](https://github.com/chatchat-space/Langchain-Chatchat/tree/master/libs/model-providers/)
引用了 [Dify](https://github.com/langgenius/dify/tree/main/api/core/model_runtime)中的相关代码。
如果您使用这部分代码并再分发，你需要包含 [ADDITIONAL_LICENSE](ADDITIONAL_LICENSE) 的完整内容。

## 联系我们

### Telegram

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white "langchain-chatchat")](https://t.me/+RjliQ3jnJ1YyN2E9)

### 项目交流群

<img src="docs/img/qr_code_109.jpg" alt="二维码" width="300" />

🎉 Langchain-Chatchat 项目微信交流群，如果你也对本项目感兴趣，欢迎加入群聊参与讨论交流。

### 公众号

<img src="docs/img/official_wechat_mp_account.png" alt="二维码" width="300" />

🎉 Langchain-Chatchat 项目官方公众号，欢迎扫码关注。

![](docs/img/logo-long-chatchat-trans-v2.png)

[![pypi badge](https://img.shields.io/pypi/v/langchain-chatchat.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/python-3.8%7C3.9%7C3.10%7C3.11-blue.svg)](https://pypi.org/project/pypiserver/)

🌍 [READ THIS IN ENGLISH](README_en.md)

📃 **LangChain-Chatchat** (原 Langchain-ChatGLM)

基于 ChatGLM 等大语言模型与 Langchain 等应用框架实现，开源、可离线部署的 RAG 与 Agent 应用项目。

---

## 目录

* [概述](README.md#概述)
* [功能介绍](README.md#功能介绍)
  * [0.3.x 功能一览](README.md#03x-版本功能一览)
  * [已支持的模型推理框架与模型](README.md#已支持的模型部署框架与模型)
* [快速上手](README.md#快速上手)
    * [pip 安装部署](README.md#pip-安装部署)
    * [源码安装部署/开发部署](README.md#源码安装部署开发部署)
    * [Docker 部署](README.md#docker-部署)
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

## 功能介绍

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
| 多模态图片对话     | ❌                                | ✅  推荐使用 qwen-vl-chat                   ||
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
|不选中任何工具，上传一个图片|图片对话|使用 qwen-vl-chat 等多模态模型|

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

### pip 安装部署

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
> pip install "langchain-chatchat[xinference]" -U
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

#### 3. 初始化项目配置与数据目录

从 0.3.1 版本起，Langchain-Chatchat 使用本地 `yaml` 文件的方式进行配置，用户可以直接查看并修改其中的内容，服务器会自动更新无需重启。

1. 设置 Chatchat 存储配置文件和数据文件的根目录（可选）
```shell
# on linux or macos
export CHATCHAT_ROOT=/path/to/chatchat_data

# on windows
set CHATCHAT_ROOT=/path/to/chatchat_data
```
若不设置该环境变量，则自动使用当前目录。

2. 执行初始化
```shell
chatchat init
```
该命令会执行以下操作：
- 创建所有需要的数据目录
- 复制 samples 知识库内容
- 生成默认 `yaml` 配置文件

3. 修改配置文件
  - 配置模型（model_settings.yaml）  
    需要根据步骤 **2. 模型推理框架并加载模型** 中选用的模型推理框架与加载的模型进行模型接入配置，具体参考 `model_settings.yaml` 中的注释。主要修改以下内容：
    ```yaml
    # 默认选用的 LLM 名称
     DEFAULT_LLM_MODEL: qwen1.5-chat

     # 默认选用的 Embedding 名称
     DEFAULT_EMBEDDING_MODEL: bge-large-zh-v1.5

    # 将 `LLM_MODEL_CONFIG` 中 `llm_model, action_model` 的键改成对应的 LLM 模型
    # 在 `MODEL_PLATFORMS` 中修改对应模型平台信息
    ```
  - 配置知识库路径（basic_settings.yaml）（可选）  
    默认知识库位于 `CHATCHAT_ROOT/data/knowledge_base`，如果你想把知识库放在不同的位置，或者想连接现有的知识库，可以在这里修改对应目录即可。
    ```yaml
    # 知识库默认存储路径
     KB_ROOT_PATH: D:\chatchat-test\data\knowledge_base

     # 数据库默认存储路径。如果使用sqlite，可以直接修改DB_ROOT_PATH；如果使用其它数据库，请直接修改SQLALCHEMY_DATABASE_URI。
     DB_ROOT_PATH: D:\chatchat-test\data\knowledge_base\info.db

     # 知识库信息数据库连接URI
     SQLALCHEMY_DATABASE_URI: sqlite:///D:\chatchat-test\data\knowledge_base\info.db
    ```
  - 配置知识库（kb_settings.yaml）（可选）

    默认使用 `FAISS` 知识库，如果想连接其它类型的知识库，可以修改 `DEFAULT_VS_TYPE` 和 `kbs_config`。

#### 4. 初始化知识库

> [!WARNING]  
> 进行知识库初始化前，请确保已经启动模型推理框架及对应 `embedding` 模型，且已按照上述**步骤3**完成模型接入配置。

```shell
chatchat kb -r
```
更多功能可以查看 `chatchat kb --help`

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

```

> [!Note]
> 知识库初始化的常见问题
>
> <details>
>
> ##### 1. Windows 下重建知识库或添加知识文件时卡住不动
> 此问题常出现于新建虚拟环境中，可以通过以下方式确认：
> 
> `from unstructured.partition.auto import partition`
>
> 如果该语句卡住无法执行，可以执行以下命令：
> ```shell
> pip uninstall python-magic-bin
> # check the version of the uninstalled package
> pip install 'python-magic-bin=={version}'
> ```
> 然后按照本节指引重新创建知识库即可。
> 
> </details>

#### 5. 启动项目

```shell
chatchat start -a
```

出现以下界面即为启动成功:

![WebUI界面](docs/img/langchain_chatchat_webui.png)

> [!WARNING]  
> 由于 chatchat 配置默认监听地址 `DEFAULT_BIND_HOST` 为 127.0.0.1, 所以无法通过其他 ip 进行访问。
>
> 如需通过机器ip 进行访问(如 Linux 系统), 需要到 `basic_settings.yaml` 中将监听地址修改为 0.0.0.0。

> </details>

### 源码安装部署/开发部署

源码安装部署请参考 [开发指南](docs/contributing/README_dev.md)

### Docker 部署
```shell
docker pull chatimage/chatchat:0.3.0-2024-0624
```
> [!important]
> 强烈建议: 使用 docker-compose 部署, 具体参考 [README_docker](docs/install/README_docker.md)


### 旧版本迁移

* 0.3.x 结构改变很大,强烈建议您按照文档重新部署. 以下指南不保证100%兼容和成功. 记得提前备份重要数据!

- 首先按照 `安装部署` 中的步骤配置运行环境，修改配置文件
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

本项目代码遵循 [Apache-2.0](LICENSE) 协议。

## 联系我们

### Telegram

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white "langchain-chatchat")](https://t.me/+RjliQ3jnJ1YyN2E9)

### 项目交流群

<img src="docs/img/qr_code_110.jpg" alt="二维码" width="300" />

🎉 Langchain-Chatchat 项目微信交流群，如果你也对本项目感兴趣，欢迎加入群聊参与讨论交流。

### 公众号

<img src="docs/img/official_wechat_mp_account.png" alt="二维码" width="300" />

🎉 Langchain-Chatchat 项目官方公众号，欢迎扫码关注。

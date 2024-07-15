### 项目简介
![](https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docs/img/logo-long-chatchat-trans-v2.png)
<a href="https://trendshift.io/repositories/329" target="_blank"><img src="https://trendshift.io/api/badge/repositories/329" alt="chatchat-space%2FLangchain-Chatchat | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

[![pypi badge](https://img.shields.io/pypi/v/langchain-chatchat.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/python-3.8%7C3.9%7C3.10%7C3.11-blue.svg)](https://pypi.org/project/pypiserver/)

🌍 [READ THIS IN ENGLISH](README_en.md)

📃 **LangChain-Chatchat** (原 Langchain-ChatGLM)

基于 ChatGLM 等大语言模型与 Langchain 等应用框架实现，开源、可离线部署的 RAG 与 Agent 应用项目。

点击[这里](https://github.com/chatchat-space/Langchain-Chatchat)了解项目详情。


### 安装

1. PYPI 安装

```shell
pip install langchain-chatchat

# or if you use xinference to provide model API:
# pip install langchain-chatchat[xinference]
```

详见这里的[安装指引](https://github.com/chatchat-space/Langchain-Chatchat/tree/master?tab=readme-ov-file#%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B)。

> 注意：chatchat请放在独立的虚拟环境中，比如conda，venv，virtualenv等
> 已知问题，不能跟xinference一起安装，会让一些插件出bug，例如文件无法上传

2. 源码安装

除了通过pypi安装外，您也可以选择使用[源码启动](https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docs/contributing/README_dev.md)。(Tips:
源码配置可以帮助我们更快的寻找bug，或者改进基础设施。我们不建议新手使用这个方式)

3. Docker

```shell
docker pull chatimage/chatchat:0.3.0-2024-0624
```

> [!important]
> 强烈建议: 使用 docker-compose 部署, 具体参考 [README_docker](https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docs/install/README_docker.md)

4. AudoDL

🌐 [AutoDL 镜像](https://www.codewithgpu.com/i/chatchat-space/Langchain-Chatchat/Langchain-Chatchat) 中 `0.3.0`
版本所使用代码已更新至本项目 `v0.3.0` 版本。

### 初始化与配置

项目运行需要特定的数据目录和配置文件，执行下列命令可以生成默认配置（您可以随时修改 yaml 配置文件）：
```shell
# set the root path where storing data.
# will use current directory if not set
export CHATCHAT_ROOT=/path/to/chatchat_data

# initialize data and yaml configuration templates
chatchat init
```

在 `CHATCHAT_ROOT` 或当前目录可以找到 `*_settings.yaml` 文件，修改这些文件选择合适的模型配置，详见[初始化](https://github.com/chatchat-space/Langchain-Chatchat/tree/master?tab=readme-ov-file#3-%E5%88%9D%E5%A7%8B%E5%8C%96%E9%A1%B9%E7%9B%AE%E9%85%8D%E7%BD%AE%E4%B8%8E%E6%95%B0%E6%8D%AE%E7%9B%AE%E5%BD%95)

### 启动服务

确保所有配置正确后（特别是 LLM 和 Embedding Model），执行下列命令创建默认知识库、启动服务：
```shell
chatchat kb -r
chatchat -a
```
如无错误将自动弹出浏览器页面。

### 更新日志：
#### 0.3.1.1 (2024-07-15)
- 修复：
  - WEBUI 中设置 system message 无效([#4491](https://github.com/chatchat-space/Langchain-Chatchat/pull/4491))
  - 模型平台不支持代理([#4492](https://github.com/chatchat-space/Langchain-Chatchat/pull/4492))
  - 移除失效的 vqa_processor & aqa_processor 工具([#4498](https://github.com/chatchat-space/Langchain-Chatchat/pull/4498))
  - prompt settings 错误导致 `KeyError: 'template'`([#4501](https://github.com/chatchat-space/Langchain-Chatchat/pull/4501))
  - searx 搜索引擎不支持中文([#4504](https://github.com/chatchat-space/Langchain-Chatchat/pull/4504))
  - init时默认去连 xinference，若默认 xinference 服务不存在会报错([#4508](https://github.com/chatchat-space/Langchain-Chatchat/issues/4508))
  - init时，调用shutil.copytree，当src与dst一样时shutil报错的问题（[#4507](https://github.com/chatchat-space/Langchain-Chatchat/pull/4507))

### 项目里程碑

+ `2023年4月`: `Langchain-ChatGLM 0.1.0` 发布，支持基于 ChatGLM-6B 模型的本地知识库问答。
+ `2023年8月`: `Langchain-ChatGLM` 改名为 `Langchain-Chatchat`，发布 `0.2.0` 版本，使用 `fastchat` 作为模型加载方案，支持更多的模型和数据库。
+ `2023年10月`: `Langchain-Chatchat 0.2.5` 发布，推出 Agent 内容，开源项目在`Founder Park & Zhipu AI & Zilliz`
  举办的黑客马拉松获得三等奖。
+ `2023年12月`: `Langchain-Chatchat` 开源项目获得超过 **20K** stars.
+ `2024年6月`: `Langchain-Chatchat 0.3.0` 发布，带来全新项目架构。

+ 🔥 让我们一起期待未来 Chatchat 的故事 ···

---

### 协议

本项目代码遵循 [Apache-2.0](LICENSE) 协议。

### 联系我们

#### Telegram

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white "langchain-chatchat")](https://t.me/+RjliQ3jnJ1YyN2E9)

### 引用

如果本项目有帮助到您的研究，请引用我们：

```
@software{langchain_chatchat,
    title        = {{langchain-chatchat}},
    author       = {Liu, Qian and Song, Jinke, and Huang, Zhiguo, and Zhang, Yuxuan, and glide-the, and Liu, Qingwei},
    year         = 2024,
    journal      = {GitHub repository},
    publisher    = {GitHub},
    howpublished = {\url{https://github.com/chatchat-space/Langchain-Chatchat}}
}
```

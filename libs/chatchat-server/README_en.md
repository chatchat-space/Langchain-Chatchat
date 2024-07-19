### Project Introduction

! []( https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docs/img/logo-long-chatchat-trans-v2.png )
<a href=" https://trendshift.io/repositories/329 " target="_blank"><img src=" https://trendshift.io/api/badge/repositories/329 " alt="chatchat-space%2FLangchain-Chatchat | Trendshift" style="width: 250px;  height: 55px; " width="250" height="55"/></a>

[![pypi badge](https://img.shields.io/pypi/v/langchain-chatchat.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/python-3.8%7C3.9%7C3.10%7C3.11-blue.svg)](https://pypi.org/project/pypiserver/)

🌍  [READ THIS IN CHINESE](README.md)

📃 **LangChain Chatchat** (formerly Langchain ChatGLM)

An open-source and offline deployable RAG and Agent application project based on major language models such as ChatGLM and application frameworks such as Langchain.
Click [here](https://github.com/chatchat-space/Langchain-Chatchat）to Understand the project details.

### Installation
1. PYPI installation
```shell
pip install langchain-chatchat

# or if you use xinference to provide model API:
# pip install langchain-chatchat[xinference]

# if you update from an old version, we suggest to run init again to update yaml templates:
# pip install -U langchain-chatchat
# chatchat init
```
Please refer to the [Installation Guide](https://github.com/chatchat-space/Langchain-Chatchat/tree/master?tab=readme-OVfile#%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B) for details.
>Attention: Chatchat should be placed in a separate virtual environment, such as conda, venv, virtualienv, etc

>Known issue, cannot be installed together with xinference, which may cause some plugins to have bugs, such as file upload issues

2. Source code installation
In addition to installing through Pypi, you can also choose to use [source code startup](https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docs/contributing/README_dev.md).

(Tips: Source code configuration can help us find bugs faster or improve infrastructure. We do not recommend beginners to use this method

3. Docker
```shell
docker pull chatimage/chatchat:0.3.1.2-2024-0720

docker pull ccr.ccs.tencentyun.com/chatchat/chatchat:0.3.1.2-2024-0720 # 国内镜像
```
> [!important]
> Strong recommendation: Use docker compose for deployment, refer to [README.docker](https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docs/install/README_docker.md) for details 
1. AudoDL
🌐  [AutoDL Image](https://www.codewithgpu.com/i/chatchat-space/Langchain-Chatchat/Langchain-Chatchat）Medium ` 0.3.0`
The code used in the version has been updated to version v0.3.0 of this project.

### Initialization and Configuration
The project requires specific data directories and configuration files for operation. The following commands can generate default configurations (you can modify the YAML configuration file at any time):
```shell
# set the root path where storing data.
# will use current directory if not set
export CHATCHAT_ROOT=/path/to/chatchat_data
# initialize data and yaml configuration templates
chatchat init
```
You can find the `*_ settings.yaml` files in CHATCHAT-ROOT or the current directory. Modify these files to select the appropriate model configuration. See [Initialization](https://github.com/chatchat-space/Langchain-Chatchat/tree/master?tab=readme-ov-file#3-%E5%88%9D%E5%A7%8B%E5%8C%96%E9%A1%B9%E7%9B%AE%E9%85%8D%E7%BD%AE%E4%B8%8E%E6%95%B0%E6%8D%AE%E7%9B%AE%E5%BD%95) for details.

### Start service
After ensuring that all configurations are correct (especially LLM and Embedding Model), execute the following commands to create the default knowledge base and start the service:
```shell
chatchat kb -r
chatchat start -a
```
If there are no errors, the browser page will automatically pop up.
### Update log:
 
#### 0.3.1.1 (2024-07-15)
- Fix:
  - Invalid system message setting in WEBUI ([# 4491](https://github.com/chatchat-space/Langchain-Chatchat/pull/4491 ))
  - The model platform does not support proxies ([# 4492](https://github.com/chatchat-space/Langchain-Chatchat/pull/4492 ))
  - Remove the invalid vqasprocessor&aqa_processor tools ([# 4498]( https://github.com/chatchat-space/Langchain-Chatchat/pull/4498 ))
  - Prompt settings error causing 'KeyError: template' ([# 4501](https://github.com/chatchat-space/Langchain-Chatchat/pull/4501 ))
  - Searx search engine does not support Chinese ([# 4504](https://github.com/chatchat-space/Langchain-Chatchat/pull/4504 ))
  - When initializing, it defaults to connecting to xinference. If the default xinference service does not exist, an error will be reported ([# 4508]( https://github.com/chatchat-space/Langchain-Chatchat/issues/4508 ))
  - When initializing, call shutil.cpytree, and when src is the same as dst, shutil will report an error ([# 4507]( https://github.com/chatchat-space/Langchain-Chatchat/pull/4507 ))
  
### Project milestones
+ April 2023: Langchain ChatGLM 0.1.0 is released, supporting local knowledge base Q&A based on ChatGLM-6B model.
+ August 2023: Langchain ChatGLM will be renamed as Langchain Chatgate and release version 0.2.0, using fastchat as the model loading solution to support more models and databases.
+ October 2023: Langchain Chatcat 0.2.5 is released, featuring Agent content and an open-source project at Founder Park&Zhipu AI&Zilliz`
The hackathon held won third prize.
+ December 2023: Langchain Chatcat open-source project receives over 20K stars
+ June 2024: Langchain Watchat 0.3.0 is released, bringing a brand new project architecture.
+  🔥  Let's look forward to the future stories of Chatchat together···
---
### LICENSE
This project code follows the Apache 2.0 (LICENSE) protocol.

### Contact Us
#### Telegram
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white "langchain-chatchat")](https://t.me/+RjliQ3jnJ1YyN2E9)

### Quoting
If this project has been helpful for your research, please cite us:
```
@software{langchain_chatchat,
title        = {{langchain-chatchat}},
author       = {Liu,  Qian and Song, Jinke, and Huang, Zhiguo, and Zhang, Yuxuan, and glide-the, and Liu, Qingwei},
year         = 2024,
journal      = {GitHub repository},
publisher    = {GitHub},
howpublished = {\url{ https://github.com/chatchat-space/Langchain-Chatchat }}
}
```

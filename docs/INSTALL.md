# 安装

## 环境检查

```shell
# 首先，确信你的机器安装了 Python 3.8 - 3.10 版本
$ python --version
Python 3.8.13

# 如果低于这个版本，可使用conda安装环境
$ conda create -p /your_path/env_name python=3.8

# 激活环境
$ source activate /your_path/env_name

# 或，conda安装，不指定路径, 注意以下，都将/your_path/env_name替换为env_name
$ conda create -n env_name python=3.8
$ conda activate env_name # Activate the environment

# 更新py库
$ pip3 install --upgrade pip

# 关闭环境
$ source deactivate /your_path/env_name

# 删除环境
$ conda env remove -p  /your_path/env_name
```

## 项目依赖

```shell
# 拉取仓库
$ git clone https://github.com/imClumsyPanda/langchain-ChatGLM.git

# 进入目录
$ cd langchain-ChatGLM

# 安装依赖
$ pip install -r requirements.txt

# 默认依赖包括基本运行环境（FAISS向量库）与API服务支持。如果要使用chromadb/milvus/pg等向量库，请将requirements.txt中相应依赖取消注释再安装。

# 如果需要webui，请安装streamlit相关依赖：
$ pip install -r requirements_webui.txt
```

注：使用 `langchain.document_loaders.UnstructuredFileLoader` 进行 `.docx` 等格式非结构化文件接入时，可能需要依据文档进行其他依赖包的安装，请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)。

## 知识库初始化与迁移

当前项目的知识库信息存储在数据库中，在正式运行项目之前请先初始化数据库（我们强烈建议您在执行操作前备份您的知识文件）。

- 如果您是第一次运行本项目，知识库尚未建立，或者配置文件中的知识库类型、嵌入模型发生变化，需要以下命令初始化或重建知识库：
    ```shell
    $ python init_database.py --recreate-vs
    ``` 

- 如果您是从"`0.1.x`"版升级过来的用户，识库已经建立，且知识库类型、嵌入模型无变化，只需以下命令将现有知识库信息添加到数据库即可：
    ```shell
    $ python init_database.py
    ``` 

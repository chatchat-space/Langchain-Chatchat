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
$ git clone https://github.com/chatchat-space/Langchain-Chatchat.git

# 进入目录
$ cd Langchain-Chatchat

# 安装全部依赖
$ pip install -r requirements.txt

# 默认依赖包括基本运行环境（FAISS向量库）。如果要使用 milvus/pg_vector 等向量库，请将 requirements.txt 中相应依赖取消注释再安装。
```

此外，为方便用户 API 与 webui 分离运行，可单独根据运行需求安装依赖包。

- 如果只需运行 API，可执行：
    ```shell
    $ pip install -r requirements_api.txt
    
    # 默认依赖包括基本运行环境（FAISS向量库）。如果要使用 milvus/pg_vector 等向量库，请将 requirements.txt 中相应依赖取消注释再安装。
    ```

- 如果只需运行 WebUI，可执行：
    ```shell
    $ pip install -r requirements_webui.txt
    ```



注：使用 `langchain.document_loaders.UnstructuredFileLoader` 进行 `.docx` 等格式非结构化文件接入时，可能需要依据文档进行其他依赖包的安装，请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)。



# 安装

## 环境检查

```shell
# 首先，确信你的机器安装了 Python 3.8 及以上版本
$ python --version
Python 3.8.13

# 如果低于这个版本，可使用conda安装环境
$ conda create -p /your_path/env_name python=3.8

# 激活环境
$ source activate /your_path/env_name

# 关闭环境
$ source deactivate /your_path/env_name

# 删除环境
$ conda env remove -p  /your_path/env_name
```

## 项目依赖

```shell
# 拉取仓库
$ git clone https://github.com/imClumsyPanda/langchain-ChatGLM.git

# 安装依赖
$ pip install -r requirements.txt
```
注：使用 `langchain.document_loaders.UnstructuredFileLoader` 进行非结构化文件接入时，可能需要依据文档进行其他依赖包的安装，请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)。
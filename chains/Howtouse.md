# 如何使用ImageBind
## 下载并安装ImageBind（参见[ImageBind](https://github.com/facebookresearch/ImageBind)）
安装在/chains/modules 文件夹下。
## 使用ImageBind生成embedding
在/chains/local_doc_qa.py文件中，使用了本地embeddings.py中Myembeddings（继承自HuggingFaceEmbeddings）。
## 其他调整
针对适配ImageBind的过程中出现的其他问题进行了部分调整。
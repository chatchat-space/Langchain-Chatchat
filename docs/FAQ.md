### 常见问题

Q1: 本项目支持哪些文件格式？

A1: 目前已测试支持 txt、docx、md、pdf 格式文件，更多文件格式请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)。目前已知文档中若含有特殊字符，可能存在文件无法加载的问题。

---

Q2: 使用过程中 Python 包 `nltk`发生了 `Resource punkt not found.`报错，该如何解决？

A2: 方法一：https://github.com/nltk/nltk_data/raw/gh-pages/packages/tokenizers/punkt.zip 中的 `packages/tokenizers` 解压，放到  `nltk_data/tokenizers` 存储路径下。

`nltk_data` 存储路径可以通过 `nltk.data.path` 查询。

方法二：执行python代码

```
import nltk
nltk.download()
```

---

Q3: 使用过程中 Python 包 `nltk`发生了 `Resource averaged_perceptron_tagger not found.`报错，该如何解决？

A3: 方法一：将 https://github.com/nltk/nltk_data/blob/gh-pages/packages/taggers/averaged_perceptron_tagger.zip 下载，解压放到 `nltk_data/taggers` 存储路径下。

`nltk_data` 存储路径可以通过 `nltk.data.path` 查询。

方法二：执行python代码

```
import nltk
nltk.download()
```

---

Q4: 本项目可否在 colab 中运行？

A4: 可以尝试使用 chatglm-6b-int4 模型在 colab 中运行，需要注意的是，如需在 colab 中运行 Web UI，需将 `webui.py`中 `demo.queue(concurrency_count=3).launch( server_name='0.0.0.0', share=False, inbrowser=False)`中参数 `share`设置为 `True`。

---

Q5: 在 Anaconda 中使用 pip 安装包无效如何解决？

A5: 此问题是系统环境问题，详细见  [在Anaconda中使用pip安装包无效问题](在Anaconda中使用pip安装包无效问题.md)

---

Q6: 本项目中所需模型如何下载至本地？

A6: 本项目中使用的模型均为 `huggingface.com`中可下载的开源模型，以默认选择的 `chatglm-6b`和 `text2vec-large-chinese`模型为例，下载模型可执行如下代码：

```shell
# 安装 git lfs
$ git lfs install

# 下载 LLM 模型
$ git clone https://huggingface.co/THUDM/chatglm-6b /your_path/chatglm-6b

# 下载 Embedding 模型
$ git clone https://huggingface.co/GanymedeNil/text2vec-large-chinese /your_path/text2vec

# 模型需要更新时，可打开模型所在文件夹后拉取最新模型文件/代码
$ git pull
```

---

Q7: `huggingface.com`中模型下载速度较慢怎么办？

A7: 可使用本项目用到的模型权重文件百度网盘地址：

- ernie-3.0-base-zh.zip 链接: https://pan.baidu.com/s/1CIvKnD3qzE-orFouA8qvNQ?pwd=4wih
- ernie-3.0-nano-zh.zip 链接: https://pan.baidu.com/s/1Fh8fgzVdavf5P1omAJJ-Zw?pwd=q6s5
- text2vec-large-chinese.zip 链接: https://pan.baidu.com/s/1sMyPzBIXdEzHygftEoyBuA?pwd=4xs7
- chatglm-6b-int4-qe.zip 链接: https://pan.baidu.com/s/1DDKMOMHtNZccOOBGWIOYww?pwd=22ji
- chatglm-6b-int4.zip 链接: https://pan.baidu.com/s/1pvZ6pMzovjhkA6uPcRLuJA?pwd=3gjd
- chatglm-6b.zip 链接: https://pan.baidu.com/s/1B-MpsVVs1GHhteVBetaquw?pwd=djay

---

Q8: 下载完模型后，如何修改代码以执行本地模型？

A8: 模型下载完成后，请在 [configs/model_config.py](../configs/model_config.py) 文件中，对 `embedding_model_dict`和 `llm_model_dict`参数进行修改，如把 `llm_model_dict`从

```python
embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec": "GanymedeNil/text2vec-large-chinese"
}
```

修改为

```python
embedding_model_dict = {
                        "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
                        "ernie-base": "nghuyong/ernie-3.0-base-zh",
                        "text2vec": "/Users/liuqian/Downloads/ChatGLM-6B/text2vec-large-chinese"
}
```

---

Q9: 执行 `python cli_demo.py`过程中，显卡内存爆了，提示 "OutOfMemoryError: CUDA out of memory"

A9: 将 `VECTOR_SEARCH_TOP_K` 和 `LLM_HISTORY_LEN` 的值调低，比如 `VECTOR_SEARCH_TOP_K = 5` 和 `LLM_HISTORY_LEN = 2`，这样由 `query` 和 `context` 拼接得到的 `prompt` 会变短，会减少内存的占用。或者打开量化，请在 [configs/model_config.py](../configs/model_config.py) 文件中，对`LOAD_IN_8BIT`参数进行修改

---

Q10: 执行 `pip install -r requirements.txt` 过程中遇到 python 包，如 langchain 找不到对应版本的问题

A10: 更换 pypi 源后重新安装，如阿里源、清华源等，网络条件允许时建议直接使用 pypi.org 源，具体操作命令如下：

```shell
# 使用 pypi 源
$ pip install -r requirements.txt -i https://pypi.python.org/simple
```

或

```shell
# 使用阿里源
$ pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/
```

或

```shell
# 使用清华源
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

---

Q11: 启动 api.py 时 upload_file 接口抛出 `partially initialized module 'charset_normalizer' has no attribute 'md__mypyc' (most likely due to a circular import)`

A11: 这是由于 charset_normalizer 模块版本过高导致的，需要降低低 charset_normalizer 的版本,测试在 charset_normalizer==2.1.0 上可用。

---

Q12: 调用api中的 `bing_search_chat` 接口时，报出 `Failed to establish a new connection: [Errno 110] Connection timed out`

A12: 这是因为服务器加了防火墙，需要联系管理员加白名单，如果公司的服务器的话，就别想了GG--!

---

Q13: 加载 chatglm-6b-int8 或 chatglm-6b-int4 抛出 `RuntimeError: Only Tensors of floating point andcomplex dtype can require gradients`

A13: 疑为 chatglm 的 quantization 的问题或 torch 版本差异问题，针对已经变为 Parameter 的 torch.zeros 矩阵也执行 Parameter 操作，从而抛出 `RuntimeError: Only Tensors of floating point andcomplex dtype can require gradients`。解决办法是在 chatglm 项目的原始文件中的 quantization.py 文件 374 行改为：

```
    try:
        self.weight =Parameter(self.weight.to(kwargs["device"]), requires_grad=False)
    except Exception as e:
        pass
```

    如果上述方式不起作用，则在.cache/hugggingface/modules/目录下针对chatglm项目的原始文件中的quantization.py文件执行上述操作，若软链接不止一个，按照错误提示选择正确的路径。

注：虽然模型可以顺利加载但在cpu上仍存在推理失败的可能：即针对每个问题，模型一直输出gugugugu。

    因此，最好不要试图用cpu加载量化模型，原因可能是目前python主流量化包的量化操作是在gpu上执行的,会天然地存在gap。

---

Q14: 修改配置中路径后，加载 text2vec-large-chinese 依然提示 `WARNING: No sentence-transformers model found with name text2vec-large-chinese. Creating a new one with MEAN pooling.`

A14: 尝试更换 embedding，如 text2vec-base-chinese，请在 [configs/model_config.py](../configs/model_config.py) 文件中，修改 `text2vec-base`参数为本地路径，绝对路径或者相对路径均可


---

Q15: 使用pg向量库建表报错

A15: 需要手动安装对应的vector扩展(连接pg执行 CREATE EXTENSION IF NOT EXISTS vector)

---

Q16: pymilvus 连接超时

A16.pymilvus版本需要匹配和milvus对应否则会超时参考pymilvus==2.1.3
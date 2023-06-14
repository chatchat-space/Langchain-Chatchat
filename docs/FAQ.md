### 常见问题

Q1: 本项目支持哪些文件格式？

A1: 目前已测试支持 txt、docx、md、pdf 格式文件，更多文件格式请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)。目前已知文档中若含有特殊字符，可能存在文件无法加载的问题。

---

Q2: 执行 `pip install -r requirements.txt` 过程中，安装 `detectron2` 时发生报错怎么办？

A2: 如果不需要对 `pdf` 格式文件读取，可不安装 `detectron2`；如需对 `pdf` 文件进行高精度文本提取，建议按照如下方法安装：

```commandline
$ git clone https://github.com/facebookresearch/detectron2.git
$ cd detectron2
$ pip install -e .
```

---

Q3: 使用过程中 Python 包 `nltk`发生了 `Resource punkt not found.`报错，该如何解决？

A3: 方法一：https://github.com/nltk/nltk_data/raw/gh-pages/packages/tokenizers/punkt.zip 中的 `packages/tokenizers` 解压，放到  `nltk_data/tokenizers` 存储路径下。

`nltk_data` 存储路径可以通过 `nltk.data.path` 查询。

方法二：执行python代码

```
import nltk
nltk.download()
```

---

Q4: 使用过程中 Python 包 `nltk`发生了 `Resource averaged_perceptron_tagger not found.`报错，该如何解决？

A4: 方法一：将 https://github.com/nltk/nltk_data/blob/gh-pages/packages/taggers/averaged_perceptron_tagger.zip 下载，解压放到 `nltk_data/taggers` 存储路径下。

`nltk_data` 存储路径可以通过 `nltk.data.path` 查询。

方法二：执行python代码

```
import nltk
nltk.download()
```

---

Q5: 本项目可否在 colab 中运行？

A5: 可以尝试使用 chatglm-6b-int4 模型在 colab 中运行，需要注意的是，如需在 colab 中运行 Web UI，需将 `webui.py`中 `demo.queue(concurrency_count=3).launch( server_name='0.0.0.0', share=False, inbrowser=False)`中参数 `share`设置为 `True`。

---

Q6: 在 Anaconda 中使用 pip 安装包无效如何解决？

A6: 此问题是系统环境问题，详细见  [在Anaconda中使用pip安装包无效问题](在Anaconda中使用pip安装包无效问题.md)

---

Q7: 本项目中所需模型如何下载至本地？

A7: 本项目中使用的模型均为 `huggingface.com`中可下载的开源模型，以默认选择的 `chatglm-6b`和 `text2vec-large-chinese`模型为例，下载模型可执行如下代码：

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

Q8: `huggingface.com`中模型下载速度较慢怎么办？

A8: 可使用本项目用到的模型权重文件百度网盘地址：

- ernie-3.0-base-zh.zip 链接: https://pan.baidu.com/s/1CIvKnD3qzE-orFouA8qvNQ?pwd=4wih
- ernie-3.0-nano-zh.zip 链接: https://pan.baidu.com/s/1Fh8fgzVdavf5P1omAJJ-Zw?pwd=q6s5
- text2vec-large-chinese.zip 链接: https://pan.baidu.com/s/1sMyPzBIXdEzHygftEoyBuA?pwd=4xs7
- chatglm-6b-int4-qe.zip 链接: https://pan.baidu.com/s/1DDKMOMHtNZccOOBGWIOYww?pwd=22ji
- chatglm-6b-int4.zip 链接: https://pan.baidu.com/s/1pvZ6pMzovjhkA6uPcRLuJA?pwd=3gjd
- chatglm-6b.zip 链接: https://pan.baidu.com/s/1B-MpsVVs1GHhteVBetaquw?pwd=djay

---

Q9: 下载完模型后，如何修改代码以执行本地模型？

A9: 模型下载完成后，请在 [configs/model_config.py](../configs/model_config.py) 文件中，对 `embedding_model_dict`和 `llm_model_dict`参数进行修改，如把 `llm_model_dict`从

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

Q10: 执行 `python cli_demo.py`过程中，显卡内存爆了，提示"OutOfMemoryError: CUDA out of memory"

A10: 将 `VECTOR_SEARCH_TOP_K` 和 `LLM_HISTORY_LEN` 的值调低，比如 `VECTOR_SEARCH_TOP_K = 5` 和 `LLM_HISTORY_LEN = 2`，这样由 `query` 和 `context` 拼接得到的 `prompt` 会变短，会减少内存的占用。

---

Q11: 执行 `pip install -r requirements.txt` 过程中遇到 python 包，如 langchain 找不到对应版本的问题

A11: 更换 pypi 源后重新安装，如阿里源、清华源等，网络条件允许时建议直接使用 pypi.org 源，具体操作命令如下：

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

Q12 启动api.py时upload_file接口抛出 `partially initialized module 'charset_normalizer' has no attribute 'md__mypyc' (most likely due to a circular import)`

这是由于 charset_normalizer模块版本过高导致的，需要降低低charset_normalizer的版本,测试在charset_normalizer==2.1.0上可用。

---

Q13 启动api.py时upload_file接口，上传PDF或图片时，抛出OSError: [Errno 101] Network is unreachable

某些情况下,linux系统上的ip在请求下载ch_PP-OCRv3_rec_infer.tar等文件时，可能会抛出OSError: [Errno 101] Network is unreachable，此时需要首先修改anaconda3/envs/[虚拟环境名]/lib/[python版本]/site-packages/paddleocr/ppocr/utils/network.py脚本，将57行的：

```
download_with_progressbar(url, tmp_path)
```

修改为：

```
        try:
            download_with_progressbar(url, tmp_path)
        except Exception as e:
            print(f"download {url} error,please download it manually:")
            print(e)
```

然后按照给定网址，如"https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_rec_infer.tar"手动下载文件，上传到对应的文件夹中，如“.paddleocr/whl/rec/ch/ch_PP-OCRv3_rec_infer/ch_PP-OCRv3_rec_infer.tar”.

---

Q14 调用api中的 `bing_search_chat`接口时，报出 `Failed to establish a new connection: [Errno 110] Connection timed out`

这是因为服务器加了防火墙，需要联系管理员加白名单，如果公司的服务器的话，就别想了GG--!

# 基于本地知识的 ChatGLM 应用实现

## 介绍

🌍 [_READ THIS IN ENGLISH_](README_en.md)

🤖️ 一种利用 [ChatGLM-6B](https://github.com/THUDM/ChatGLM-6B) + [langchain](https://github.com/hwchase17/langchain) 实现的基于本地知识的 ChatGLM 应用。

💡 受 [GanymedeNil](https://github.com/GanymedeNil) 的项目 [document.ai](https://github.com/GanymedeNil/document.ai) 和 [AlexZhangji](https://github.com/AlexZhangji) 创建的 [ChatGLM-6B Pull Request](https://github.com/THUDM/ChatGLM-6B/pull/216) 启发，建立了全部基于开源模型实现的本地知识问答应用。

✅ 本项目中 Embedding 选用的是 [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese/tree/main)，LLM 选用的是 [ChatGLM-6B](https://github.com/THUDM/ChatGLM-6B)。依托上述模型，本项目可实现全部使用**开源**模型**离线私有部署**。

⛓️ 本项目实现原理如下图所示，过程包括加载文件 -> 读取文本 -> 文本分割 -> 文本向量化 -> 问句向量化 -> 在文本向量中匹配出与问句向量最相似的`top k`个 -> 匹配出的文本作为上下文和问题一起添加到`prompt`中 -> 提交给`LLM`生成回答。

![实现原理图](img/langchain+chatglm.png)

🚩 本项目未涉及微调、训练过程，但可利用微调或训练对本项目效果进行优化。

## 更新信息

**[2023/04/15]**
1. 重构项目结构，在根目录下保留命令行 Demo [cli_demo.py](cli_demo.py) 和 Web UI Demo [webui.py](webui.py)；
2. 对 Web UI 进行改进，修改为运行 Web UI 后首先按照 [configs/model_config.py](configs/model_config.py) 默认选项加载模型，并增加报错提示信息等；
3. 对常见问题进行补充说明。

**[2023/04/12]**
1. 替换 Web UI 中的样例文件，避免出现 Ubuntu 中出现因文件编码无法读取的问题；
2. 替换`knowledge_based_chatglm.py`中的 prompt 模版，避免出现因 prompt 模版包含中英双语导致 chatglm 返回内容错乱的问题。

**[2023/04/11]** 
1. 加入 Web UI V0.1 版本（感谢 [@liangtongt](https://github.com/liangtongt)）；
2. `README.md`中增加常见问题（感谢 [@calcitem](https://github.com/calcitem) 和 [@bolongliu](https://github.com/bolongliu)）；
3. 增加 LLM 和 Embedding 模型运行设备是否可用`cuda`、`mps`、`cpu`的自动判断。
4. 在`knowledge_based_chatglm.py`中增加对`filepath`的判断，在之前支持单个文件导入的基础上，现支持单个文件夹路径作为输入，输入后将会遍历文件夹中各个文件，并在命令行中显示每个文件是否成功加载。

**[2023/04/09]**
1. 使用`langchain`中的`RetrievalQA`替代之前选用的`ChatVectorDBChain`，替换后可以有效减少提问 2-3 次后因显存不足而停止运行的问题；
2. 在`knowledge_based_chatglm.py`中增加`EMBEDDING_MODEL`、`VECTOR_SEARCH_TOP_K`、`LLM_MODEL`、`LLM_HISTORY_LEN`、`REPLY_WITH_SOURCE`参数值设置；
3. 增加 GPU 显存需求更小的`chatglm-6b-int4`、`chatglm-6b-int4-qe`作为 LLM 模型备选项；
4. 更正`README.md`中的代码错误（感谢 [@calcitem](https://github.com/calcitem)）。

**[2023/04/07]** 
1. 解决加载 ChatGLM 模型时发生显存占用为双倍的问题 (感谢 [@suc16](https://github.com/suc16) 和 [@myml](https://github.com/myml)) ；
2. 新增清理显存机制；
3. 新增`nghuyong/ernie-3.0-nano-zh`和`nghuyong/ernie-3.0-base-zh`作为 Embedding 模型备选项，相比`GanymedeNil/text2vec-large-chinese`占用显存资源更少 (感谢 [@lastrei](https://github.com/lastrei))。

## 使用方式

### 硬件需求
- ChatGLM-6B 模型硬件需求
  
    | **量化等级**   | **最低 GPU 显存**（推理） | **最低 GPU 显存**（高效参数微调） |
    | -------------- | ------------------------- | --------------------------------- |
    | FP16（无量化） | 13 GB                     | 14 GB                             |
    | INT8           | 8 GB                     | 9 GB                             |
    | INT4           | 6 GB                      | 7 GB                              |

- Embedding 模型硬件需求

    本项目中默认选用的 Embedding 模型 [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese/tree/main) 约占用显存 3GB，也可修改为在 CPU 中运行。

### 软件需求

本项目已在 Python 3.8，CUDA 11.7 环境下完成测试。

### 1. 安装环境

- 环境检查

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

- 项目依赖

```shell
# 拉取仓库
$ git clone https://github.com/imClumsyPanda/langchain-ChatGLM.git

# 安装依赖
$ pip install -r requirements.txt
```
注：使用 langchain.document_loaders.UnstructuredFileLoader 进行非结构化文件接入时，可能需要依据文档进行其他依赖包的安装，请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)

### 2. 设置模型默认参数

在开始执行 Web UI 或命令行交互前，请先检查 [configs/model_config.py](configs/model_config.py) 中的各项模型参数设计是否符合需求。

### 3. 执行脚本体验 Web UI 或命令行交互
执行 [webui.py](webui.py) 脚本体验 **Web 交互**
```shell
$ python webui.py
```
注：如未将模型下载至本地，请执行前检查`$HOME/.cache/huggingface/`文件夹剩余空间，至少15G

执行后效果如下图所示：
![webui](img/ui1.png)
Web UI 可以实现如下功能：

1. 运行前自动读取`configs/model_config.py`中`LLM`及`Embedding`模型枚举及默认模型设置运行模型，如需重新加载模型，可在界面重新选择后点击`重新加载模型`进行模型加载；
2. 可手动调节保留对话历史长度，可根据显存大小自行调节
3. 添加上传文件功能，通过下拉框选择已上传的文件，点击`加载文件`按钮，过程中可随时更换加载的文件

或执行 [knowledge_based_chatglm.py](cli_demo.py) 脚本体验**命令行交互**
```shell
$ python knowledge_based_chatglm.py
```


### 常见问题
Q1: 本项目支持哪些文件格式？

A1: 目前已测试支持 txt、docx、md、pdf 格式文件，更多文件格式请参考 [langchain 文档](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/unstructured_file.html)。目前已知文档中若含有特殊字符，可能存在文件无法加载的问题。

Q3: 使用过程中 Python 包`nltk`发生了`Resource punkt not found.`报错，该如何解决？

A3: https://github.com/nltk/nltk_data/raw/gh-pages/packages/tokenizers/punkt.zip 中的 `packages/tokenizers` 解压，放到  `nltk_data/tokenizers` 存储路径下。

 `nltk_data` 存储路径可以通过 `nltk.data.path` 查询。

Q4: 使用过程中 Python 包`nltk`发生了`Resource averaged_perceptron_tagger not found.`报错，该如何解决？

A4: 将 https://github.com/nltk/nltk_data/blob/gh-pages/packages/taggers/averaged_perceptron_tagger.zip 下载，解压放到 `nltk_data/taggers` 存储路径下。

 `nltk_data` 存储路径可以通过 `nltk.data.path` 查询。

Q5: 本项目可否在 colab 中运行？

A5: 可以尝试使用 chatglm-6b-int4 模型在 colab 中运行，需要注意的是，如需在 colab 中运行 Web UI，需将`webui.py`中`demo.queue(concurrency_count=3).launch(
    server_name='0.0.0.0', share=False, inbrowser=False)`中参数`share`设置为`True`。

Q6: 在 Anaconda 中使用 pip 安装包无效如何解决？

A6: 此问题是系统环境问题，详细见  [在Anaconda中使用pip安装包无效问题](docs/在Anaconda中使用pip安装包无效问题.md)

Q7: 本项目中所需模型如何下载至本地？

A7: 本项目中使用的模型均为`huggingface.com`中可下载的开源模型，以默认选择的`chatglm-6b`和`text2vec-large-chinese`模型为例，下载模型可执行如下代码：

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

Q8: `huggingface.com`中模型下载速度较慢怎么办？

A8: 可使用本项目用到的模型权重文件百度网盘地址：
- ernie-3.0-base-zh.zip 链接: https://pan.baidu.com/s/1CIvKnD3qzE-orFouA8qvNQ?pwd=4wih
- ernie-3.0-nano-zh.zip 链接: https://pan.baidu.com/s/1Fh8fgzVdavf5P1omAJJ-Zw?pwd=q6s5
- text2vec-large-chinese.zip 链接: https://pan.baidu.com/s/1sMyPzBIXdEzHygftEoyBuA?pwd=4xs7
- chatglm-6b-int4-qe.zip 链接: https://pan.baidu.com/s/1DDKMOMHtNZccOOBGWIOYww?pwd=22ji
- chatglm-6b-int4.zip 链接: https://pan.baidu.com/s/1pvZ6pMzovjhkA6uPcRLuJA?pwd=3gjd
- chatglm-6b.zip 链接: https://pan.baidu.com/s/1B-MpsVVs1GHhteVBetaquw?pwd=djay

Q9: 下载完模型后，如何修改代码以执行本地模型？

A9: 模型下载完成后，请在 [configs/model_config.py](configs/model_config.py) 文件中，对`embedding_model_dict`和`llm_model_dict`参数进行修改，如把`embedding_model_dict`从
```
embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec": "GanymedeNil/text2vec-large-chinese"
}
```

修改为

```
embedding_model_dict = {
                        "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
                        "ernie-base": "nghuyong/ernie-3.0-base-zh",
                        "text2vec": "/Users/liuqian/Downloads/ChatGLM-6B/text2vec-large-chinese"
}
```

## DEMO

以问题`chatglm-6b 的局限性具体体现在哪里，如何实现改进`为例

未使用 langchain 接入本地文档时：

>ChatGLM-6B 是一个基于 GPT-3 的聊天机器人,它的局限性主要体现在以下几个方面:
>1. 语言模型的精度:GPT-3 是一种大型的语言模型,它的精度比较高,但是仍然有一些局限性。例如,它可能无法准确地理解某些方言、口音或者复杂的句子结构。
>2. 知识图谱的完整性:GPT-3 可以生成一些知识图谱,但是其完整性和准确性可能不够。例如,它可能无法准确地理解某些领域的专业知识和术语。
>3. 对话生成的连贯性:GPT-3 可以生成一些连贯的对话,但是其生成的对话可能不够自然。例如,它可能会生成一些虚假的、不连贯的对话或者误解用户的意图。
>
>为了改进 ChatGLM-6B,可以考虑以下几个方面:
>1. 提高语言模型的精度:可以通过增加训练数据、使用更好的语言模型架构、优化模型训练过程等方式来提高语言模型的精度。
>2. 增强知识图谱的完整性:可以通过增加知识图谱的维度、使用更好的知识图谱构建方法、优化知识图谱的匹配算法等方式来增强知识图谱的完整性。
>3. 提高对话生成的连贯性:可以通过增加对话生成模型的上下文信息、使用更好的上下文信息提取方法、优化对话生成模型的算法等方式来提高对话生成的连贯性。
>4. 引入更多的人类反馈:人类反馈可以帮助 ChatGLM-6B 更好地理解用户的意图和需求,从而提高对话生成的质量和准确性。可以通过引入更多的人类客服、使用人类反馈收集器等方式来引入更多的人类反馈。

使用 langchain 接入 ChatGLM-6B 项目的 README.md 文件后 ChatGLM 的回答：
>ChatGLM-6B 是一个基于深度学习的自然语言处理模型,它在回答问题方面表现出色。但是,它也有一些局限性,具体如下:
>1. 语言理解有限:ChatGLM-6B 只学习了中文自然语言,对于其他语言可能会存在理解上的局限性。
>2. 知识储备不足:ChatGLM-6B 的训练数据集只包含了中文语料,因此它可能无法回答一些非中文的问题或者某些特定领域的问题。
>3. 数据量有限:ChatGLM-6B 的训练数据集只有几百万条记录,因此它可能无法回答一些非常具体或者复杂的问题。
>
>为了改进 ChatGLM-6B,可以考虑以下几个方面:
>1. 学习更多的语言知识:可以学习其他语言的自然语言处理技术,扩大语言理解的范围。
>2. 扩大知识储备:可以收集更多的中文语料,或者使用其他语言的数据集来扩充知识储备。
>3. 增加数据量:可以使用更大的数据集来训练 ChatGLM-6B,提高模型的表现。
>4. 引入更多的评估指标:可以引入更多的评估指标来评估模型的表现,从而发现 ChatGLM-6B 存在的不足和局限性。
>5. 改进模型架构:可以改进 ChatGLM-6B 的模型架构,提高模型的性能和表现。例如,可以使用更大的神经网络或者改进的卷积神经网络结构。

## 路线图
- [x] 实现 langchain + ChatGLM-6B 本地知识应用
- [x] 基于 langchain 实现非结构化文件接入
  - [x] .md
  - [x] .pdf(需要按照常见问题 Q2 中描述进行`detectron2`的安装)
  - [x] .docx
  - [x] .txt
  - [ ] 搜索引擎与本地网页
- [ ] 增加更多 LLM 模型支持
  - [x] THUDM/chatglm-6b
  - [x] THUDM/chatglm-6b-int4
  - [x] THUDM/chatglm-6b-int4-qe
- [ ] 增加 Web UI DEMO
  - [x] 利用 gradio 实现 Web UI DEMO
  - [x] 添加输出内容及错误提示
  - [ ] 引用标注
- [ ] 利用 fastapi 实现 API 部署方式，并实现调用 API 的 web ui DEMO

## 项目交流群
![二维码](img/qr_code_4.jpg)

🎉 langchain-ChatGLM 项目交流群，如果你也对本项目感兴趣，欢迎加入群聊参与讨论交流。

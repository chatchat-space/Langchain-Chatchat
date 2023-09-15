## 如何自定义分词器

### 在哪里写，哪些文件要改
1. 在```text_splitter```文件夹下新建一个文件，文件名为您的分词器名字，比如`my_splitter.py`，然后在`__init__.py`中导入您的分词器，如下所示：
```python
from .my_splitter import MySplitter
```

2. 修改```config/model_config.py```文件，将您的分词器名字添加到```text_splitter_dict```中，如下所示：
```python
MySplitter: {
        "source": "huggingface",  ## 选择tiktoken则使用openai的方法
        "tokenizer_name_or_path": "your tokenizer", #如果选择huggingface则使用huggingface的方法，部分tokenizer需要从Huggingface下载
    }
TEXT_SPLITTER = "MySplitter"
```

完成上述步骤后，就能使用自己的分词器了。

### 如何贡献您的分词器

1. 将您的分词器所在的代码文件放在```text_splitter```文件夹下，文件名为您的分词器名字，比如`my_splitter.py`，然后在`__init__.py`中导入您的分词器。
2. 发起PR，并说明您的分词器面向的场景或者改进之处。我们非常期待您能举例一个具体的应用场景。
3. 在Readme.md中添加您的分词器的使用方法和支持说明。

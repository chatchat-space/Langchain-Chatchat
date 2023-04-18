## 变更日志

**[2023/04/15]**

1. 重构项目结构，在根目录下保留命令行 Demo [cli_demo.py](../cli_demo.py) 和 Web UI Demo [webui.py](../webui.py)；
2. 对 Web UI 进行改进，修改为运行 Web UI 后首先按照 [configs/model_config.py](../configs/model_config.py) 默认选项加载模型，并增加报错提示信息等；
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
# fastchat 调用实现教程
langchain-ChatGLM 现已支持通过调用 FastChat API 进行 LLM 调用，支持的 API 形式为 **OpenAI API 形式**。 
1. 首先请参考 [FastChat 官方文档](https://github.com/lm-sys/FastChat/blob/main/docs/openai_api.md#restful-api-server) 进行 FastChat OpenAI 形式 API 部署
2. 依据 FastChat API 启用时的 `model_name` 和 `api_base` 链接，在本项目的 `configs/model_config.py` 的 `llm_model_dict` 中增加选项。如：
    ```python
    llm_model_dict = {
            
        # 通过 fastchat 调用的模型请参考如下格式
        "fastchat-chatglm-6b": {
            "name": "chatglm-6b",  # "name"修改为fastchat服务中的"model_name"
            "pretrained_model_name": "chatglm-6b",
            "local_model_path": None,
            "provides": "FastChatOpenAILLM",  # 使用fastchat api时，需保证"provides"为"FastChatOpenAILLM"
            "api_base_url": "http://localhost:8000/v1"  # "name"修改为fastchat服务中的"api_base_url"
        },
    }
    ```
    其中 `api_base_url` 根据 FastChat 部署时的 ip 地址和端口号得到，如 ip 地址设置为 `localhost`，端口号为 `8000`，则应设置的 `api_base_url` 为 `http://localhost:8000/v1`

3. 将 `configs/model_config.py` 中的 `LLM_MODEL` 修改为对应模型名。如：
    ```python
    LLM_MODEL = "fastchat-chatglm-6b"
    ```
4. 根据需求运行 `api.py`, `cli_demo.py` 或 `webui.py`。
### 开始使用

> 环境配置完成后，启动步骤为先启动chatchat-server，然后启动chatchat-frontend。
> chatchat可通过pypi安装一键启动，您也可以选择使用[源码启动](README_dev.md)。(Tips:源码配置可以帮助我们更快的寻找bug，或者改进基础设施。我们不建议新手使用这个方式)

#### pypi安装一键启动
- 安装chatchat
```shell
pip install langchain-chatchat -U
```

> 工作空间配置
> 
> 操作指令` chatchat-config` 
```text 
options:
     
    -h, --help            show this help message and exit
    -v {true,false}, --verbose {true,false}
    是否开启详细日志
    -d DATA, --data DATA  数据存放路径
    -f FORMAT, --format FORMAT
    日志格式
    --clear               清除配置
    --show               显示配置
``` 
> 查看配置
```shell
 chatchat-config --show                                                                                               ±[●●][dev_config_init]
{
    "log_verbose": false,
    "CHATCHAT_ROOT": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat",
    "DATA_PATH": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat/data",
    "IMG_DIR": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat/img",
    "NLTK_DATA_PATH": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat/data/nltk_data",
    "LOG_FORMAT": "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    "LOG_PATH": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat/data/logs",
    "MEDIA_PATH": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat/data/media",
    "BASE_TEMP_DIR": "/media/gpt4-pdf-chatbot-langchain/langchain-ChatGLM/libs/chatchat-server/chatchat/data/temp",
    "class_name": "ConfigBasic"
}

```

### 模型服务配置
 如果您已经有了一个openai endpoint的能力的地址，可以在`configs._model_config.py`文件中MODEL_PLATFORMS直接配置
   - platform_name 可以任意填写，不要重复即可
   - platform_type 以后可能根据平台类型做一些功能区分,与platform_name一致即可
   - 将框架部署的模型填写到对应列表即可。不同框架可以加载同名模型，项目会自动做负载均衡。

### 自定义平台加载
可以通过 model_providers 提供转换不同平台的接口为openai endpoint的能力
> 配置*CHATCHAT_ROOT*文件夹configs中的`model_providers.yaml`文件，即可完成自定义平台加载
```shell
 
vim model_providers.yaml
```
> 
> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`
> 
> 详细配置请参考[README.md](../model-providers/README.md)

### 初始化知识库
```shell
chatchat-kb -r
```

### 启动服务
```shell
chatchat -a
```

### 模型？
```text
chatchat 0.3版本中，为保证平台、模型、及本地服务的兼容，在保证可扩展性的同时，
我们对模型的加载进行了重新设计. chatchat 0.3之后的版本，我们将分离模型加载和服务启动. 您可以使用提供了`openaiEndpoint`任何服务,
可以在`configs._model_config.py`文件中MODEL_PLATFORMS直接配置
 
```

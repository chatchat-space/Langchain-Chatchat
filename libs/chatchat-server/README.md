### 开始使用

> 环境配置完成后，启动步骤为先启动chatchat-server，然后启动chatchat-frontend。
> chatchat可通过pypi安装一键启动，您也可以选择使用[源码启动](../../docs/contributing/README_dev.md)。(Tips:
> 源码配置可以帮助我们更快的寻找bug，或者改进基础设施。我们不建议新手使用这个方式)

#### pypi安装一键启动

- 安装chatchat

```shell
pip install langchain-chatchat -U
```

> 注意：chatchat请放在独立的虚拟环境中，比如conda，venv，virtualenv等
>
> 已知问题，不能跟xf一起安装，会让一些插件出bug，例如文件无法上传

> 工作空间配置
>
> 操作指令` chatchat-config`

```text 
 
Usage: chatchat-config [OPTIONS] COMMAND [ARGS]...

  指令` chatchat-config` 工作空间配置

Options:
  --help  Show this message and exit.

Commands:
  basic   基础配置
  kb      知识库配置
  model   模型配置
  server  服务配置

``` 

### 模型服务配置

如果您已经有了一个openai endpoint的能力的地址，可以在MODEL_PLATFORMS这里直接配置
```text
chatchat-config model --set_model_platforms TEXT      模型平台配置 as a JSON string.
```
- platform_name 可以任意填写，不要重复即可
- platform_type 以后可能根据平台类型做一些功能区分,与platform_name一致即可
- 将框架部署的模型填写到对应列表即可。不同框架可以加载同名模型，项目会自动做负载均衡。
- 设置模型
```shell
$ chatchat-config model --set_model_platforms "[{
    \"platform_name\": \"xinference\",
    \"platform_type\": \"xinference\",
    \"api_base_url\": \"http://127.0.0.1:9997/v1\",
    \"api_key\": \"EMPT\",
    \"api_concurrencies\": 5,
    \"llm_models\": [
        \"autodl-tmp-glm-4-9b-chat\"
    ],
    \"embed_models\": [
        \"bge-large-zh-v1.5\"
    ],
    \"image_models\": [],
    \"reranking_models\": [],
    \"speech2text_models\": [],
    \"tts_models\": []
}]"
```

### 初始化知识库

```shell
chatchat-kb -r
```

### 启动服务

```shell
chatchat -a
```

### 模型？
 
chatchat 0.3版本中，为保证平台、模型、及本地服务的兼容，在保证可扩展性的同时，
我们对模型的加载进行了重新设计. chatchat 0.3之后的版本，我们将分离模型加载和服务启动. 
您可以使用提供了`openaiEndpoint`任何服务,在MODEL_PLATFORMS这里直接配置
```text
chatchat-config model --set_model_platforms TEXT      模型平台配置 as a JSON string.
```
- platform_name 可以任意填写，不要重复即可
- platform_type 以后可能根据平台类型做一些功能区分,与platform_name一致即可
- 将框架部署的模型填写到对应列表即可。不同框架可以加载同名模型，项目会自动做负载均衡。

  

### 部署手册

移步这里 [xinference环境配置手册](../../docs/install/README_xinference.md)

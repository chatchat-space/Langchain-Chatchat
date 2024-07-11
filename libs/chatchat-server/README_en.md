### Getting Started

> After the environment configuration is complete, the startup steps are to start chatchat-server first, and then
> chatchat-frontend.
> chatchat can be installed through pypi and started with one click. You can also choose to
> use [source code startup](../../docs/contributing/README_dev.md). (Tips: Source code configuration can help us find
> bugs
> faster or improve infrastructure. We do not recommend this method for novices)

#### One-click start for pypi installation

- Install chatchat

```shell
pip install langchain-chatchat -U
```

> Note: Chatchat should be placed in an independent virtual environment, such as conda, venv, virtualenv, etc.
>
> Known issues, cannot be installed with xf, will cause some plugins to have bugs, such as files cannot be uploaded

> Workspace configuration
>
> Operation command ` chatchat-config`

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

## Model service configuration

If you already have an address with the capability of an OpenAI endpoint, you can directly configure it in MODEL_PLATFORMS as follows:

```text
chatchat-config model --set_model_platforms TEXT      Configure model platforms as a JSON string.
```
- `platform_name` can be arbitrarily filled, just ensure it is unique.
- `platform_type` might be used in the future for functional distinctions based on platform types, so it should match the platform_name.
- List the models deployed on the framework in the corresponding list. Different frameworks can load models with the same name, and the project will automatically balance the load.
- Set up the model

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
    \"text2image_models\": [],
    \"image2text_models\": [],
    \"rerank_models\": [],
    \"speech2text_models\": [],
    \"text2speech_models\": []
}]"
```

## Initialize knowledge base

```shell
chatchat-kb -r
```

### Start service

```shell
chatchat -a
```

### Model?

In version 0.3 of chatchat, to ensure compatibility across platforms, models, 
and local services while maintaining scalability, we have redesigned the model loading process. 
From chatchat 0.3 onwards, we will separate model loading from service startup. 
You can use any service that provides openaiEndpoint and directly configure it 
in MODEL_PLATFORMS as follows:
```text 
chatchat-config model --set_model_platforms TEXT      Configure model platforms as a JSON string.

```
- `platform_name` can be arbitrarily filled, just ensure it is unique.
- `platform_type` might be used in the future for functional distinctions based on platform types, so it should match the platform_name.
- List the models deployed on the framework in the corresponding list. Different frameworks can load models with the same name, and the project will automatically balance the load.



### Deployment manual

Check here [xinference environment configuration manual](../../docs/install/README_xinference_en.md)

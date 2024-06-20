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

If you already have an openai endpoint capability address, you can directly configure it in
the `configs._model_config.py` file MODEL_PLATFORMS

- platform_name can be filled in arbitrarily, just don't repeat it
- platform_type may make some functional distinctions based on platform type in the future, just be consistent with
  platform_name
- Fill in the model deployed by the framework into the corresponding list. Different frameworks can load models with the
  same name, and the project will automatically do load balancing.

### Custom platform loading

You can use model_providers to provide the ability to convert interfaces of different platforms to openai endpoints
> Configure the `model_providers.yaml` file in the *CHATCHAT_ROOT* folder configs to complete the custom platform
> loading

```shell

vim model_providers.yaml
```

>
> Note: Before you configure the platform, please confirm that the platform dependencies are complete. For example, for
> the Zhipu platform, you need to install the Zhipu SDK `pip install zhipuai`
>
> For detailed configuration, please refer to [README.md](../model-providers/README_en.md)

## Initialize knowledge base

```shell
chatchat-kb -r
```

### Start service

```shell
chatchat -a
```

### Model?

```text
In chatchat 0.3, to ensure compatibility of platform, model, and local service, while ensuring scalability,
we redesigned the model loading. After chatchat 0.3, we will separate model loading and service startup. You can use any service that provides `openaiEndpoint`,
you can directly configure MODEL_PLATFORMS in the `configs._model_config.py` file

```

### Deployment manual

Check here [xinference environment configuration manual](../../docs/install/README_xinference_en.md)

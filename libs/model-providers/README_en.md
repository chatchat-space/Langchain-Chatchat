### Get started

When the project is installed, configure this `model_providers.yaml` file to complete the platform loading
> Note: Before you configure the platform, please confirm that the platform dependencies are complete. For example, for
> the Zhipu platform, you need to install the Zhipu SDK `pip install zhipuai`

model_providers contains the global configuration `provider_credential` and model configuration `model_credential`
provided by different platforms

The configurations loaded by different platforms are different. For how to configure this file

Please refer to the platform `yaml` file under the package `model_providers.core.model_runtime.model_providers`
For a detailed description of the design of `schemas` information, please refer
to [README.md](model_providers/core/model_runtime/README_en.md)

### Related platform configuration instructions

#### To load the xinference platform, do the following

- Check `schemas` information

[xinference.yaml](model_providers/core/model_runtime/model_providers/xinference/xinference.yaml) contains the following
information:
`supported_model_types` describes the supported `llm`, `text-embedding`, and `rerank` model types
`configurate_methods` describes the variable `customizable-model`, indicating that this is a platform for customizing
models
`model_credential_schema` describes the credential information required for custom models

- Install SDK

```shell
pip install xinference-client
```

- Edit `model_providers.yaml`

```yaml


xinference:
  model_credential:
    - model: 'chatglm3-6b'
      model_type: 'llm'
      model_credentials:
        server_url: 'http://127.0.0.1:9997/'
        model_uid: 'chatglm3-6b'

```

#### To load the ollama platform, do the following

- View `schemas` information

The following information is included
in [ollama.yaml](model_providers/core/model_runtime/model_providers/ollama/ollama.yaml),

`supported_model_types` describes the supported model types `llm` and `text-embedding`

`configurate_methods` describes the variables

- `customizable-model` indicates that this is a platform that can customize the model

`model_credential_schema` describes the credentials required for the custom model

- Install the sdk

```shell
$ pip install openai
```

- Edit `model_providers.yaml`

```yaml


ollama:
  model_credential:
    - model: 'llama3'
      model_type: 'llm'
      model_credentials:
        base_url: 'http://172.21.192.1:11434/v1'

```

#### To load the openai platform, do the following

- View `schemas` information

The following information is included
in [openai.yaml](Fmodel_providers/core/model_runtime/model_providers/openai/openai.yaml),

`supported_model_types` describes the supported model types `llm` and `text-embedding`

`configurate_methods` describes the variables

- `predefined-model` indicates that this is a platform that uses predefined models

- `customizable-model` indicates that this is a platform that can customize models

`model_credential_schema` describes the credentials required for custom models

`provider_credential_schema` describes the credentials of the platform

- Install SDK

```shell
$ pip install openai
```

- Edit `model_providers.yaml`

```yaml

openai:

  model_credential:
    - model: 'gpt-3.5-turbo'
      model_type: 'llm'
      model_credentials:
        openai_api_key: 'sk-'
        openai_organization: ''
        openai_api_base: ''
    - model: 'gpt-4'
      model_type: 'llm'
      model_credentials:
        openai_api_key: 'sk-'
        openai_organization: ''
        openai_api_base: ''

  provider_credential:
    openai_api_key: 'sk-'
    openai_organization: ''
    openai_api_base: ''
```

#### To load the Zhipu platform, do the following

- View `schemas` information

The following information is included
in [zhipuai.yaml](model_providers/core/model_runtime/model_providers/zhipuai/zhipuai.yaml),

`supported_model_types` describes the support of two model types, `llm` and `text-embedding`

`configurate_methods` describes the variable `predefined-model`, indicating that this is a platform using a predefined
model

`provider_credential_schema` describes the platform's credential information

- Install SDK

```shell
$ pip install zhipuai
```

- Edit `model_providers.yaml`

```yaml

zhipuai:
provider_credential:
api_key: 'd4fa0690b6dfa205204cae2e12aa6fb6.2'
```

#### To load the deepseek platform, do the following

- View `schemas` information

In [deepseek.yaml](model_providers/core/model_runtime/model_providers/deepseek/deepseek.yaml), the following information
is included:

`supported_model_types` describes the supported model types `llm` and `text-embedding`

`configurate_methods` describes the variable `predefined-model`, indicating that this is a platform using a predefined
model

`provider_credential_schema` describes the platform's credential information

- Install the sdk

```shell
$ pip install openai
```

- Edit `model_providers.yaml`

```yaml


deepseek:
  model_credential:
    - model: 'deepseek-chat'
      model_type: 'llm'
      model_credentials:
        base_url: 'https://api.deepseek.com'
        api_key: 'sk-dcb625fcbc1e497d80b7b9493b51d758'




```

### Additional License

Some of the codes in this folder refer to the relevant codes in [Dify](https://github.com/langgenius/dify/tree/main/api/core/model_runtime).
If you use this code and redistribute it, you need to include the full contents of the [ADDITIONAL_LICENSE](../../ADDITIONAL_LICENSE) .
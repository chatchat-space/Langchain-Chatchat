
### 开始使用

当项目安装完成，配置这个`model_providers.yaml`文件，即可完成平台加载
> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`

model_providers包含了不同平台提供的 全局配置`provider_credential`,和模型配置`model_credential`
不同平台所加载的配置有所不同，关于如何配置这个文件

请查看包`model_providers.core.model_runtime.model_providers`下方的平台 `yaml`文件
关于`schemas`信息详细描述设计，请查看 [README_CN.md](model_providers/core/model_runtime/README_CN.md)


### 相关平台配置说明


#### 要加载xinference平台，操作如下

- 查看`schemas`信息
  
在[xinference.yaml](model_providers/core/model_runtime/model_providers/xinference/xinference.yaml)包含了如下信息，
    `supported_model_types`描述支持了`llm`、`text-embedding`、`rerank` 模型类型
    `configurate_methods`描述包含变量 `customizable-model`表示这个是一个可以自定义模型的平台
    `model_credential_schema`描述包含了自定义模型需要的凭据信息

- 安装sdk
```shell
$ pip install xinference-client
```

- 编辑`model_providers.yaml`

```yaml


xinference:
  model_credential:
    - model: 'chatglm3-6b'
      model_type: 'llm'
      model_credentials:
        server_url: 'http://127.0.0.1:9997/'
        model_uid: 'chatglm3-6b'


```

#### 要加载ollama平台，操作如下

- 查看`schemas`信息

  在[ollama.yaml](model_providers/core/model_runtime/model_providers/ollama/ollama.yaml)包含了如下信息，
  `supported_model_types`描述支持了`llm`和`text-embedding`两种模型类型

  `configurate_methods`描述包含变量 
  - `customizable-model`表示这个是一个可以自定义模型的平台

  `model_credential_schema`描述包含了自定义模型需要的凭据信息 
- 安装sdk
```shell
$ pip install openai
```

- 编辑`model_providers.yaml`

```yaml


ollama:
  model_credential:
    - model: 'llama3'
      model_type: 'llm'
      model_credentials:
        base_url: 'http://172.21.192.1:11434/v1'

```



#### 要加载openai平台，操作如下

- 查看`schemas`信息

  在[openai.yaml](model_providers/core/model_runtime/model_providers/openai/openai.yaml)包含了如下信息，
  `supported_model_types`描述支持了`llm`和`text-embedding`两种模型类型

  `configurate_methods`描述包含变量
    - `predefined-model`表示这个是一个使用预定义模型的平台
    - `customizable-model`表示这个是一个可以自定义模型的平台

  `model_credential_schema`描述包含了自定义模型需要的凭据信息
  `provider_credential_schema`描述包含平台的凭据信息
- 安装sdk
```shell
$ pip install openai
```

- 编辑`model_providers.yaml`

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

#### 要加载智谱平台，操作如下

- 查看`schemas`信息

  在[zhipuai.yaml](model_providers/core/model_runtime/model_providers/zhipuai/zhipuai.yaml)包含了如下信息，
  `supported_model_types`描述支持了`llm`和`text-embedding`两种模型类型
  `configurate_methods`描述包含变量 `predefined-model`表示这个是一个使用预定义模型的平台
  `provider_credential_schema`描述包含平台的凭据信息

- 安装sdk
```shell
$ pip install zhipuai
```

- 编辑`model_providers.yaml`

```yaml

zhipuai:
  provider_credential:
    api_key: 'd4fa0690b6dfa205204cae2e12aa6fb6.2'
```



#### 要加载deepseek平台，操作如下

- 查看`schemas`信息

  在[deepseek.yaml](model_providers/core/model_runtime/model_providers/deepseek/deepseek.yaml)包含了如下信息，
  `supported_model_types`描述支持了`llm`和`text-embedding`两种模型类型
  `configurate_methods`描述包含变量 `predefined-model`表示这个是一个使用预定义模型的平台
  `provider_credential_schema`描述包含平台的凭据信息

- 安装sdk
```shell
$ pip install openai
```

- 编辑`model_providers.yaml`

```yaml


deepseek:
  model_credential:
    - model: 'deepseek-chat'
      model_type: 'llm'
      model_credentials:
        base_url: 'https://api.deepseek.com'
        api_key: 'sk-dcb625fcbc1e497d80b7b9493b51d758'




```

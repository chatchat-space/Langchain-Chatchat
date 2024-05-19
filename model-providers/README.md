
### 加入开发
#### 依赖管理：Poetry与env/dependency管理方法
这个项目使用 Poetry 来管理依赖。
> 注意：在安装Poetry之前，如果您使用Conda，请创建并激活一个新的Conda env（例如，`conda create-n chatchat python=3.9`）

Install Poetry: [documentation on how to install it.](https://python-poetry.org/docs/#installing-with-pipx)

> 注意: 如果您使用 Conda 或 Pyenv 作为您的环境/包管理器，在安装Poetry之后，
> 使用如下命令使Poetry使用virtualenv python environment (`poetry config virtualenvs.prefer-active-python true`)

#### 本地开发环境安装

- 选择主项目目录
```shell
cd model-providers
```

- 安装model-providers依赖(for running model-providers lint\tests):

```shell
poetry install --with lint,test
```

#### 格式化和代码检查
在提交PR之前,请在本地运行以下命令;CI系统也会进行检查。

##### 代码格式化
本项目使用ruff进行代码格式化。

要对某个库进行格式化,请在相应的库目录下运行相同的命令:
```shell
cd {model-providers|chatchat|chatchat-server|chatchat-frontend}
make format
```

此外,你可以使用format_diff命令仅对当前分支中与主分支相比已修改的文件进行格式化:


```shell
 
make format_diff
```
当你对项目的一部分进行了更改,并希望确保更改的部分格式正确,而不影响代码库的其他部分时,这个命令特别有用。



### 开始使用

当项目安装完成，配置这个`model_providers.yaml`文件，即可完成平台加载
> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`

model_providers包含了不同平台提供的 全局配置`provider_credential`,和模型配置`model_credential`
不同平台所加载的配置有所不同，关于如何配置这个文件

请查看包`model_providers.core.model_runtime.model_providers`下方的平台 `yaml`文件
关于`schemas`信息详细描述设计，请查看 [README_CN.md](model_providers/core/model_runtime/README_CN.md)


#### 相关平台配置说明


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
        base_url: 'http://172.21.80.1:11434/v1'

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

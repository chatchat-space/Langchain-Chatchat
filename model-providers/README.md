
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
例如`zhipuai.yaml`，这里给出了`provider_credential_schema`,其中包含了一个变量`api_key`

要加载智谱平台，操作如下

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

- `model-providers`可以运行pytest 测试
```shell
  poetry run pytest tests/server_unit_test/test_init_server.py

```
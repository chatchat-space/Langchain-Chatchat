# Langchain-Chatchat 源代码部署/开发部署指南

## 0. 拉取项目代码

如果您是想要使用源码启动的用户，请直接拉取 master 分支代码

```shell
git clone https://github.com/chatchat-space/Langchain-Chatchat.git
```

## 1. 初始化开发环境

Langchain-Chatchat 自 0.3.0 版本起，为方便支持用户使用 pip 方式安装部署，以及为避免环境中依赖包版本冲突等问题，
在源代码/开发部署中不再继续使用 requirements.txt 管理项目依赖库，转为使用 Poetry 进行环境管理。

### 1.1 安装 Poetry

> 在安装 Poetry 之前，如果您使用 Conda，请创建并激活一个新的 Conda 环境，例如使用 `conda create -n chatchat python=3.9` 创建一个新的 Conda 环境。

安装 Poetry: [Poetry 安装文档](https://python-poetry.org/docs/#installing-with-pipx)

> [!Note]
> 如果你没有其它 poetry 进行环境/依赖管理的项目，利用 pipx 或 pip 都可以完成 poetry 的安装，

> [!Note]
> 如果您使用 Conda 或 Pyenv 作为您的环境/包管理器，在安装Poetry之后，
> 使用如下命令使 Poetry 使用 virtualenv python environment (`poetry config virtualenvs.prefer-active-python true`)

### 1.2 安装源代码/开发部署所需依赖库

进入主项目目录，并安装 Langchain-Chatchat 依赖

```shell
cd  Langchain-Chatchat/libs/chatchat-server/
poetry install --with lint,test -E xinference

# or use pip to install in editing mode:
pip install -e .
```

> [!Note]
> Poetry install 后会在你的虚拟环境中 site-packages 路径下生成一个 chatchat-`<version>`.dist-info 文件夹带有 direct_url.json 文件，这个文件指向你的开发环境

### 1.3 更新开发部署环境依赖库

当开发环境中所需的依赖库发生变化时，一般按照更新主项目目录(`Langchain-Chatchat/libs/chatchat-server/`)下的 pyproject.toml 再进行 poetry update 的顺序执行。

### 1.4 将更新后的代码打包测试

如果需要对开发环境中代码打包成 Python 库并进行测试，可在主项目目录执行以下命令：

```shell
poetry build
```

命令执行完成后，在主项目目录下会新增 `dist` 路径，其中存储了打包后的 Python 库。

## 2. 设置源代码根目录

如果您在开发时所使用的 IDE 需要指定项目源代码根目录，请将主项目目录(`Langchain-Chatchat/libs/chatchat-server/`)设置为源代码根目录。

执行以下命令之前，请先设置当前目录和项目数据目录：
```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat
export CHATCHAT_ROOT=/parth/to/chatchat_data
```

## 3. 关于 chatchat 配置项

从 `0.3.1` 版本开始，所有配置项改为 `yaml` 文件，具体参考 [Settings](settings.md)。

执行以下命令初始化项目配置文件和数据目录：
```shell
cd libs/chatchat-server
python chatchat/cli.py init
```

## 4. 初始化知识库

> [!WARNING]
> 这个命令会清空数据库、删除已有的配置文件，如果您有重要数据，请备份。

```shell
cd libs/chatchat-server
python chatchat/cli.py kb --recreate-vs
```
如需使用其它 Embedding 模型，或者重建特定的知识库，请查看 `python chatchat/cli.py kb --help` 了解更多的参数。

## 5. 启动服务

```shell
cd libs/chatchat-server
python chatchat/cli.py start -a
```

如需调用 API，请参考 [API 使用说明](api.md)

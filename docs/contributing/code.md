
# 代码贡献
贡献此仓库的代码时，请查阅 ["fork and pull request"](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) 流程，除非您是项目的维护者。请不要直接提交到主分支。
在提交PR之前，请检查按照pull request模板的指导进行操作。注意，我们的CI系统会自动运行linting和测试，以确保您的代码符合我们的标准。
更重要的是，我们需要保持良好的单元测试和文档，如果你做了如下操作：
- 添加新功能
更新受影响的操作文档
- 修复bug
尽可能添加一个单元测试，在tests/integration_tests或tests/unit_tests中


## 依赖管理：Poetry 与 env/dependency 管理方法
这个项目使用 Poetry 来管理依赖。
> [!Note]
> 在安装 Poetry 之前，如果您使用 Conda，请创建并激活一个新的 Conda 环境，例如使用 `conda create -n chatchat python=3.9` 创建一个新的 Conda 环境。

安装 Poetry: [Poetry 安装文档](https://python-poetry.org/docs/#installing-with-pipx)

> [!Note]
> 如果你没有其它 poetry 进行环境/依赖管理的项目，利用 pipx 或 pip 都可以完成 poetry 的安装，

> [!Note]
> 如果您使用 Conda 或 Pyenv 作为您的环境/包管理器，在安装Poetry之后，
> 使用如下命令使 Poetry 使用 virtualenv python environment (`poetry config virtualenvs.prefer-active-python true`)


## 本地开发环境安装

- 选择主项目目录
```shell
cd  Langchain-Chatchat/libs/chatchat-server/
```

- 安装chatchat依赖(for running chatchat lint\tests):

```shell
poetry install --with lint,test
```
>  Poetry install后会在你的site-packages安装一个chatchat-`<version>`.dist-info文件夹带有direct_url.json文件，这个文件指向你的开发环境

## 格式化和代码检查
在提交PR之前,请在本地运行以下命令;CI系统也会进行检查。

### 代码格式化
本项目使用ruff进行代码格式化。

### 关于

要对某个库进行格式化,请在相应的库目录下运行相同的命令:
```shell
cd {chatchat-server|chatchat-frontend}
make format
```

此外,你可以使用format_diff命令仅对当前分支中与主分支相比已修改的文件进行格式化:

```shell
make format_diff
```
当你对项目的一部分进行了更改,并希望确保更改的部分格式正确,而不影响代码库的其他部分时,这个命令特别有用。

 

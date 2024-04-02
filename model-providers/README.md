
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

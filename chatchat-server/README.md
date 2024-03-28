
### 加入开发
#### 依赖管理：Poetry与env/dependency管理方法
这个项目使用 Poetry 来管理依赖。 
> 注意：在安装Poetry之前，如果您使用Conda，请创建并激活一个新的Conda env（例如，`conda create-n chatchat python=3.9`）

Install Poetry: [documentation on how to install it.](https://python-poetry.org/docs/#installing-with-pipx)

> 注意: 如果您使用 Conda 或 Pyenv 作为您的环境/包管理器，在安装Poetry之后， 
> 使用如下命令使Poetry使用virtualenv python environment (`poetry config virtualenvs.prefer-active-python true`)

#### 本地开发环境安装

- 选择主项目目录
```
cd chatchat
```

- 安装chatchat依赖(for running chatchat lint\tests):

```
poetry install --with lint,test
```
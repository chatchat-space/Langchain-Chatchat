
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
cd chatchat
```

- 安装chatchat依赖(for running chatchat lint\tests):

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

> 环境配置完成后，启动步骤为先启动chatchat-server，然后启动chatchat-frontend。
> chatchat可通过pypi安装一键启动，您也可以选择使用源码启动。

#### pypi安装一键启动
- 安装chatchat
```shell
pip install langchain-chatchat -U
```
- 复制配置文件

 ```shell
cd chatchat-server/
mkdir ~/.config/chatchat/
cp -r configs ~/.config/chatchat/
cp -r data ~/.config/chatchat/
cp -r img ~/.config/chatchat/
```

> 当项目安装完成，配置这个`model_providers.yaml`文件，即可完成自定义平台加载
> 
> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`
> 
> 详细配置请参考[README.md](../model-providers/README.md)

 
- 启动服务
```shell
chatchat  -a
```



#### 源码启动chatchat-server
- 初始化依赖
```shell
cd chatchat-server/chatchat
python copy_config_example.py
```
- 初始化仓库
```shell
cd chatchat-server/chatchat
python init_database.py
```
- 启动服务
```shell
python chatchat-server/chatchat/startup.py -a
```

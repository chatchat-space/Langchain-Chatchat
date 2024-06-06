### 开始使用

> 环境配置完成后，启动步骤为先启动chatchat-server，然后启动chatchat-frontend。
> chatchat可通过pypi安装一键启动，您也可以选择使用源码启动。(Tips:源码配置可以帮助我们更快的寻找bug，或者改进基础设施。我们不建议新手使用这个方式)

#### pypi安装一键启动
- 安装chatchat
```shell
pip install langchain-chatchat -U
```
- 复制配置文件
> 后面我们会提供一个一键初始化的脚本，现在您可以手动复制配置文件
> 请注意：这个命令会清空数据库，如果您有重要数据，请备份
```shell
cd chatchat-server/chatchat
mkdir -p ~/.config/chatchat/
cp -r configs ~/.config/chatchat/
cp -r data ~/.config/chatchat/
cp -r img ~/.config/chatchat/
```

> 当配置文件复制完成后，配置拷贝后路径的`model_providers.yaml`文件，即可完成自定义平台加载
```shell
cd ~/.config/chatchat/configs
vim model_providers.yaml
```
> 
> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`
> 
> 详细配置请参考[README.md](../model-providers/README.md)

- 启动服务
```shell
chatchat -a
```

#### 源码启动chatchat-server
- 安装chatchat
```shell
git clone https://github.com/chatchat-space/Langchain-Chatchat.git
```
- 修改`model_providers.yaml`文件，即可完成自定义平台加载
 ```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat/configs
vim model_providers.yaml
```
- 平台配置
> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`
> 
> 详细配置请参考[README.md](../model-providers/README.md)


- 初始化开发环境
 
> [Code](../../docs/contributing/code.md): 源码配置可以帮助我们更快的寻找bug，或者改进基础设施。

- 初始化仓库
> 请注意：这个命令会清空数据库，如果您有重要数据，请备份
```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat
python init_database.py --recreate-vs
```
- 启动服务
```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat
python startup.py -a
```
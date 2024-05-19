 
### 开始使用

> 环境配置完成后，启动步骤为先启动chatchat-server，然后启动chatchat-frontend。
> chatchat可通过pypi安装一键启动，您也可以选择使用源码启动。

#### pypi安装一键启动
- 安装chatchat
```shell
pip install langchain-chatchat -U
```
- 复制配置文件
> 后面我们会提供一个一键初始化的脚本，现在您可以手动复制配置文件
> 请注意：这个命令会清空数据库，如果您有重要数据，请备份
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
 
- 初始化仓库
> 请注意：这个命令会清空数据库，如果您有重要数据，请备份
```shell
cd chatchat-server/chatchat
python init_database.py
```
- 启动服务
```shell
python chatchat-server/chatchat/startup.py -a
```

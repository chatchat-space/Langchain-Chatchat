#### 源码启动chatchat-server

- 安装chatchat

```shell
git clone https://github.com/chatchat-space/Langchain-Chatchat.git
```

- 初始化开发环境

> [Code](code.md): 源码配置可以帮助我们更快的寻找bug，或者改进基础设施。

- 关于chatchat-config

> chatchat-config由ConfigWorkSpace接口提供知识库配置载入存储
>
> 具体实现可以参考basic_config.py
>

- ConfigWorkSpace接口说明

```text
ConfigWorkSpace是一个配置工作空间的抽象类，提供基础的配置信息存储和读取功能。
提供ConfigFactory建造方法产生实例。
该类的实例对象用于存储工作空间的配置信息，如工作空间的路径等
工作空间的配置信息存储在用户的家目录下的.chatchat/workspace/workspace_config.json文件中。
注意：不存在则读取默认
```

- 关于`model_providers.yaml`文件，是平台配置文件

> 我们抽象了不同平台提供的 全局配置`provider_credential`,和模型配置`model_credential`

> 关于设计文稿，请查看 [README_CN.md](../../libs/model-providers/model_providers/core/model_runtime/README)

- 平台配置

> 注意: 在您配置平台之前，请确认平台依赖完整，例如智谱平台，您需要安装智谱sdk `pip install zhipuai`
>
> 详细配置请参考[README.md](../../libs/model-providers/README.md)

- 初始化仓库(使用默认 embedding 模型)

> 请注意：这个命令会清空数据库，如果您有重要数据，请备份

```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat
python init_database.py --recreate-vs
```

- 初始化仓库(指定 embedding 模型)

```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat
python init_database.py --recreate-vs --embed-model=text-embedding-3-small # embedding 模型名称
```

- 启动服务

```shell
cd Langchain-Chatchat/libs/chatchat-server/chatchat
python startup.py -a
```

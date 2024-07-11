### chatchat 数据库对话配置说明

#### 一、使用建议

> 1. 因大模型生成的sql可能与预期有偏差，请务必在测试环境中进行充分测试、评估；
> 2. 生产环境中，对于查询操作，由于不确定查询效率，推荐数据库采用主从数据库架构，让text2sql连接从数据库，防止可能的慢查询影响主业务；
> 3. 对于写操作应保持谨慎，如不需要写操作，设置read_only为True,最好再从数据库层面收回数据库用户的写权限，防止用户通过自然语言对数据库进行修改操作；
> 4. text2sql与大模型在意图理解、sql转换等方面的能力有关，可切换不同大模型进行测试；
> 5. 数据库表名、字段名应与其实际作用保持一致、容易理解，且应对数据库表名、字段进行详细的备注说明，帮助大模型更好理解数据库结构；
> 6. 若现有数据库表名难于让大模型理解，可配置table_comments字段，补充说明某些表的作用。

#### 二、配置说明

##### 1. 配置节点
初始化后，在tool_settings.yaml文件中，找到text2sql配置节点：


```yaml
text2sql:
  model_name: qwen-plus
  use: false
  sqlalchemy_connect_str: mysql+pymysql://用户名:密码@主机地址/数据库名称
  read_only: false
  top_k: 50
  return_intermediate_steps: true
  table_names: []
  table_comments: {}
```

##### 2. 主要参数解释
1. **model_name**

  该工具需单独指定使用的大模型，与用户前端选择使用的模型无关

2. **sqlalchemy_connect_str**

  SQLAlchemy连接字符串，支持的数据库有：crate、duckdb、googlesql、mssql、mysql、mariadb、oracle、postgresql、sqlite、clickhouse、prestodb

  不同的数据库请查阅SQLAlchemy用法，修改sqlalchemy_connect_str，配置对应的数据库连接，如sqlite为sqlite:///数据库文件路径

  如提示缺少对应数据库的驱动，请自行通过poetry安装

3. **read_only**

  设置为true会开启只读模式。但我们仍然强烈推荐优先从数据库层面对用户权限进行限制

4. **top_k**

  限定返回的行数

5. **table_names**

  如果不指定table_names，会先使用SQLDatabaseSequentialChain，这个链会先预测需要哪些表，然后再将相关表输入SQLDatabaseChain，这是因为如果不指定table_names，直接使用SQLDatabaseChain，Langchain会将全量表结构传递给大模型，可能会因token太长从而引发错误，也浪费资源，但如果表很多，SQLDatabaseSequentialChain也会使用很多token

  如果指定了table_names，直接使用SQLDatabaseChain，将特定表结构传递给大模型进行判断，可节约一定资源。
  使用特定表的示例如下：

  ```yaml
    table_names: ["sys_user","sys_dept"]
  ```

6. **table_comments**


   如果出现大模型选错表的情况，可尝试根据实际情况额外声明表名和对应的说明，例如：

  ```yaml
    table_comments: {"tableA":"这是一个用户表，存储了用户的基本信息","tanleB":"角色表"}
  ```

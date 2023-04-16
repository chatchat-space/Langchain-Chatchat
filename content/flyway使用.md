---
author: 技术平台部
---
# flyway使用

## 1. 添加pom
  
```
<dependency>
    <groupId>com.dragonsoft</groupId>
    <artifactId>duceap-boot-starter-flyway</artifactId>
</dependency>
```

##  2. 配置说明

```
#flayway自动执行[true：开启（默认）、false:关闭]
duceap.flyway.enabled=true
#默认根据驱动名进行自动匹配，同时可以显示通过flyway.dbtype指定数据库类型
#duceap.flyway.dbtype=mysql
#当没有配置flyway脚本扫描器类，默认加载此目录下flyway脚本,sql/oracle可不配置，只配置模块名即可。多个逗号隔开
duceap.flyway.locations=classpath:/sql/mysql/
#同时可指定加载classpath、filesystem下的flyway脚本，如下：
#duceap.flyway.locations=classpath:/sql/oracle/DUCEAP/
###############其他默认配置######################
#duceap.flyway.placeholderPrefix=#{
#duceap.flyway.placeholderSuffix=}
#duceap.flyway.outOfOrder=true
#duceap.flyway.initOnMigrate=true
#duceap.flyway.initVersion=0.5.0
#duceap.flyway.ignoreFailedFutureMigration=false
#数据表空间
#duceap.flyway.placeholders.TABLESPACE_DATA=USERS
#索引表空间
#duceap.flyway.placeholders.TABLESPACE_INDEX=USERS
#大字段表空间
#duceap.flyway.placeholders.TABLESPACE_LOB=USERS
```

> 在 duceap.flyway.locations的路径下配置sql

## 3. flyway脚本编写规范

- flyway脚本放置目录
  -  默认存放于resources/sql/{dbtype}/{modelPrefix}目录下其中dbtype为数据库类型，如mysql、oralce、postgresql、h2,由平台自动识别;modelPrefix 业务系统名/模块名，如 DUCEAP/uploader、DCUC

- flyway脚本命名规则
  - 脚本按照flyway规范命名，如：sql/{DBtype}/{modelPrefix}/V2_1_0001__Init_table.sql如上版本为2.1.0001，__后用于描述脚本内容，多个脚本按版本号递增，业务系统版本号建议从2.0开始，避免与平台的脚本版本号冲突
  
- flyway脚本执行顺序
  - 以V2_1_0001__Init_table.sql为例，首先判断SQL版本号，V2_1_0001__Init_table.sql版本号为2_1,由低版本开始执行，如先执行2_0的脚本文件，再执行2_1的脚本文件。
  - 当脚本文件相同时，比较版本号后的数字编号，有低到高开始执行。

![](./assets/flyway使用/2022-06-09-16-06-30.png)

  - 前缀分隔符为固定前缀分隔符，代表数据库版本化；
    - V：每个文件只会被执行一次
    - R：校验和变化了就会执行
  - 2_1 为 SQL 脚本版本，’_’ 翻译为小数点，2_1 即为 2.1 版本；
  - __为两个下划线，代表中间分隔符；
  - init_table 为 SQL 脚本名，概述本脚本要进行的操作；
  - .sql 为固定后缀。

## 命令行工具

windows cli.bat  
linux cli.sh

## 命令列表

### llm 管理

llm 支持列表

```shell
cli.bat llm ls
```

### embedding 管理

embedding 支持列表

```shell
cli.bat embedding ls
```

### start 启动管理

查看启动选择
```shell
cli.bat start
```

```shell
cli.bat start
```

启动命令行交互

```shell
cli.bat start cli
```

启动Web 交互

```shell
cli.bat start webui
```

启动api服务

```shell
cli.bat start api 
```

可以设置使用配置文件的方式(配置文件在当前工程目录忽略后缀.yaml输入)
```shell
cli.bat start api -c api_config
```


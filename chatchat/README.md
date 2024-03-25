
### 加入开发
项目需要使用python3.9打包,如果您有conda环境我们建议您使用它创建一个新的python3.9环境。

#### 安装 Poetry
Install Poetry: [documentation on how to install it.](https://python-poetry.org/docs/#installing-with-pipx)

#### 本地开发环境安装

- 选择主项目目录
```
cd chatchat
```

- 安装chatchat依赖(for running chatchat lint\tests):

```
poetry install --with lint,test
```

### 仓库结构
如果您想要贡献代码，您需要了解仓库的结构。这将有助于您找到您想要的文件，以及了解如何将您的代码提交到仓库。

chatchat沿用了 monorepo的组织方式, 项目的代码库包含了多个包。

以下是可视化为树的结构：


```shell
.
├── docker 
├── docs  # 文档 
├── frontend  # 前端
├── libs
│   ├── chatchat-server  # 服务端
│   │    └── tests
│   │        ├── integration_tests # 集成测试 （每个包都有，为了简洁没有展示）
│   │        └── unit_tests # 单元测试 （每个包都有，为了简洁没有展示）

 

```
根目录还包含以下文件：

pyproject.toml: 用于构建文档和文档linting的依赖项，cookbook。
Makefile: 包含用于构建，linting和文档和cookbook的快捷方式的文件。

根目录中还有其他文件，但它们的都应该是顾名思义的，请查看相应的文件夹以了解更多信息。

### 代码

代码库中的代码分为两个部分：

- libs/chatchat-server目录包含chatchat服务端代码。
- frontend目录包含chatchat前端代码。

详细的

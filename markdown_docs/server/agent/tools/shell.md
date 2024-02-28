## FunctionDef shell(query)
**shell**: shell函数的功能是执行一个shell查询并返回结果。

**参数**:
- query: 字符串类型，表示要执行的shell查询命令。

**代码描述**:
该shell函数定义在`server/agent/tools/shell.py`文件中，是项目中用于执行shell命令的核心函数。函数接收一个名为`query`的字符串参数，该参数是需要执行的shell命令。函数内部首先创建了一个`ShellTool`类的实例`tool`，然后调用这个实例的`run`方法执行传入的`query`命令。最终，函数返回`run`方法的执行结果。

在项目的结构中，虽然`server/agent/tools/__init__.py`和`server/agent/tools_select.py`这两个文件中没有直接的代码示例或文档说明如何调用`shell`函数，但可以推断，`shell`函数作为工具模块中的一部分，可能会被项目中的其他部分调用以执行特定的shell命令。这种设计使得执行shell命令的逻辑被封装在一个单独的函数中，便于维护和重用。

**注意**:
- 在使用`shell`函数时，需要确保传入的`query`命令是安全的，避免执行恶意代码。
- 该函数的执行结果取决于`ShellTool`类的`run`方法如何实现，因此需要了解`ShellTool`的具体实现细节。

**输出示例**:
假设`ShellTool`的`run`方法简单地返回执行命令的输出，如果调用`shell("echo Hello World")`，那么可能的返回值为：
```
Hello World
```
## ClassDef ShellInput
**ShellInput**: ShellInput类的功能是定义一个用于封装Shell命令的数据模型。

**属性**:
- query: 一个字符串类型的属性，用于存储可以在Linux命令行中执行的Shell命令。该属性通过Field方法定义，其中包含一个描述信息，说明这是一个可执行的Shell命令。

**代码描述**:
ShellInput类继承自BaseModel，这表明它是一个基于Pydantic库的模型，用于数据验证和管理。在这个类中，定义了一个名为`query`的属性，这个属性必须是一个字符串。通过使用Field方法，为`query`属性提供了一个描述，即“一个能在Linux命令行运行的Shell命令”，这有助于理解该属性的用途和功能。

在项目的上下文中，虽然当前提供的信息没有直接展示ShellInput类如何被其他对象调用，但可以推断，ShellInput类可能被用于封装用户输入或者其他来源的Shell命令，之后这些封装好的命令可能会在项目的其他部分，如服务器的代理工具中被执行。这样的设计使得Shell命令的处理更加模块化和安全，因为Pydantic模型提供了一层数据验证，确保只有合法和预期的命令才会被执行。

**注意**:
- 使用ShellInput类时，需要确保传入的`query`字符串是有效且安全的Shell命令。考虑到Shell命令的强大功能和潜在的安全风险，应当避免执行来自不可信源的命令。
- 由于ShellInput类基于Pydantic库，使用该类之前需要确保项目中已经安装了Pydantic。此外，熟悉Pydantic库的基本使用和数据验证机制将有助于更有效地利用ShellInput类。

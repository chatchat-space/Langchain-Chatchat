## FunctionDef launch_api(args, args_list, log_name)
**launch_api**: 此函数的功能是启动API服务。

**参数**:
- args: 包含API启动所需参数的对象，此对象应具备访问如api_host和api_port等属性的能力。
- args_list: 一个字符串列表，默认值为api_args，指定了需要转换为命令行参数的键名。
- log_name: 日志文件的名称。如果未提供，则根据API的主机名和端口动态生成。

**代码描述**:
`launch_api` 函数首先打印出启动API服务的提示信息，包括中英文两种语言。接着，如果没有提供`log_name`参数，函数会根据API服务的主机名和端口号生成日志文件的名称，并将其存储在预定义的日志路径下。然后，函数通过调用`string_args`函数，将`args`对象中的参数转换成命令行可接受的字符串格式。`string_args`函数的详细功能和使用方法已在相关文档中描述。

之后，`launch_api`函数构建了一个用于启动API服务的shell命令字符串，该字符串包含了启动脚本的名称（`api.py`）、转换后的参数字符串以及日志文件的路径。最后，使用`subprocess.run`方法执行构建的shell命令，以在后台启动API服务，并将标准输出和标准错误重定向到日志文件中。

在整个过程中，`launch_api`函数还会打印出日志文件的位置信息，以便于在API服务启动异常时，用户可以轻松地找到并查看日志文件。

**在项目中的调用关系**:
`launch_api` 函数在项目中负责启动API服务的核心功能。它通过调用`string_args`函数来处理命令行参数的转换，这显示了`launch_api`与`string_args`之间的直接依赖关系。`string_args`函数为`launch_api`提供了参数字符串化的能力，使得`launch_api`能够有效地构建用于启动API服务的shell命令。

**注意**:
- 确保传递给`launch_api`函数的`args`对象包含了所有必要的API启动参数，如`api_host`和`api_port`。
- 如果`log_name`参数未提供，日志文件的命名将依赖于API服务的主机名和端口号，因此请确保这些信息的准确性。
- 在使用`launch_api`函数时，应确保相关的API启动脚本（`api.py`）存在于预期的路径下，并且能够正确处理通过命令行传递的参数。
## FunctionDef launch_webui(args, args_list, log_name)
**launch_webui**: 此函数的功能是启动webui服务。

**参数**:
- args: 包含启动webui所需参数的对象。此对象应具备访问各参数值的能力。
- args_list: 参数列表，默认值为web_args，用于指定哪些参数需要被包含在最终生成的命令行字符串中。
- log_name: 日志文件的名称。如果未提供，则默认使用LOG_PATH路径下的webui作为日志文件名。

**代码描述**:
`launch_webui` 函数主要负责启动webui服务。首先，函数打印出启动webui的提示信息，既包括英文也包括中文，以确保用户了解当前操作。接着，函数检查是否提供了`log_name`参数，如果没有提供，则使用默认的日志文件名。

接下来，函数调用`string_args`函数，将`args`对象中的参数转换为命令行可接受的字符串格式。这一步骤是通过检查`args`对象中的参数与`args_list`列表中指定的参数键名，生成最终的参数字符串。

根据`args`对象中的`nohup`参数值，`launch_webui`函数决定是否以后台模式启动webui服务。如果`nohup`为真，则构造一个命令行字符串，该字符串将webui服务的输出重定向到指定的日志文件，并在后台运行。否则，直接构造一个命令行字符串以前台模式运行webui服务。

最后，使用`subprocess.run`方法执行构造好的命令行字符串，启动webui服务。函数在webui服务启动后打印出完成提示信息。

**在项目中的调用关系**:
`launch_webui` 函数在项目中负责启动webui服务的任务。它依赖于`string_args`函数来处理命令行参数的生成。`string_args`函数根据提供的参数对象和参数列表，生成适用于命令行的参数字符串。这种设计使得`launch_webui`函数能够灵活地处理不同的启动参数，同时保持命令行参数生成逻辑的集中和一致性。

**注意**:
- 确保传递给`launch_webui`函数的`args`对象中包含了所有必要的参数，特别是`nohup`参数，因为它决定了webui服务是以前台模式还是后台模式运行。
- 如果在后台模式下运行webui服务，务必检查指定的日志文件，以便于排查可能出现的启动异常。

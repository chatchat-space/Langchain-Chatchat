## FunctionDef list_running_models(controller_address, placeholder)
**list_running_models**: 此函数的功能是从fastchat controller获取已加载模型列表及其配置项。

**参数**:
- `controller_address`: 字符串类型，Fastchat controller服务器地址。如果未提供，则会尝试从`fschat_controller_address()`函数获取默认地址。
- `placeholder`: 字符串类型，该参数未使用，仅作为占位符。

**代码描述**:
`list_running_models`函数首先检查`controller_address`参数是否提供，如果未提供，则调用`fschat_controller_address()`函数获取Fastchat控制器的默认地址。随后，函数使用`get_httpx_client()`函数创建一个HTTP客户端实例，并向`controller_address`指定的地址发送POST请求，请求路径为`/list_models`。请求成功后，从响应中解析出模型列表，并对每个模型调用`get_model_config()`函数获取其配置项，最后将模型及其配置项以字典形式包装在`BaseResponse`对象中返回。

在异常处理方面，如果在执行过程中遇到任何异常，函数会记录错误信息，并返回一个`code`为500的`BaseResponse`对象，同时在`msg`字段中提供错误详情。

**注意**:
- 确保提供的`controller_address`是有效的Fastchat控制器地址，否则无法成功获取模型列表。
- 该函数依赖于`get_httpx_client()`和`get_model_config()`函数，确保这些依赖函数能够正常工作。
- 函数使用POST请求与Fastchat控制器通信，确保控制器支持`/list_models`路径的处理。
- 在处理异常时，函数会记录详细的错误信息，有助于调试和问题定位。

**输出示例**:
```python
{
    "code": 200,
    "msg": "success",
    "data": {
        "model1": {
            "model_version": "1.0",
            "language": "English",
            // 其他配置项
        },
        "model2": {
            "model_version": "2.0",
            "language": "Chinese",
            // 其他配置项
        }
        // 更多模型及其配置项
    }
}
```
此示例展示了函数调用成功时可能返回的响应格式，其中`data`字段包含了每个模型及其配置项的详细信息，而`code`和`msg`字段表示请求处理成功。
## FunctionDef list_config_models(types, placeholder)
**list_config_models**: 此函数的功能是从本地获取configs中配置的模型列表。

**参数**:
- `types`: 类型为`List[str]`，默认值为`["local", "online"]`。此参数用于指定需要获取的模型配置项类别，例如`local`、`online`、`worker`等。
- `placeholder`: 类型为`str`，默认值为`None`。此参数为占位用，调用时无实际效果，主要用于API设计的扩展性。

**代码描述**:
`list_config_models`函数首先定义了一个空字典`data`，用于存储最终的模型配置信息。函数通过调用`list_config_llm_models`函数获取所有配置的大型语言模型（LLM）的不同类型。然后，函数遍历这些模型类型，如果模型类型存在于`types`参数中，则通过调用`get_model_config`函数获取每个模型的详细配置信息，并将这些信息添加到`data`字典中。最后，函数返回一个`BaseResponse`对象，其中`data`字段包含了根据`types`参数筛选后的模型配置信息。

**注意**:
- 在使用此函数时，需要确保`types`参数中包含的模型类型已经在系统中正确配置，否则可能无法获取到预期的配置信息。
- 此函数通过`BaseResponse`对象返回数据，确保了API响应的一致性和标准化。调用方可以通过检查`BaseResponse`对象中的`code`和`msg`字段来判断请求处理的状态和结果。

**输出示例**:
```python
{
    "code": 200,
    "msg": "success",
    "data": {
        "local": {
            "model1": {
                "config1": "value1",
                "config2": "value2"
            },
            "model2": {
                "config1": "value1",
                "config2": "value2"
            }
        },
        "online": {
            "model3": {
                "config1": "value1",
                "config2": "value2"
            },
            "model4": {
                "config1": "value1",
                "config2": "value2"
            }
        }
    }
}
```
此输出示例展示了函数调用成功时可能返回的响应格式，其中`data`字段包含了根据`types`参数筛选后的模型配置信息，而`code`和`msg`字段表示请求处理成功。
## FunctionDef get_model_config(model_name, placeholder)
**get_model_config**: 此函数的功能是获取LLM模型的配置项（合并后的）。

**参数**:
- `model_name`: 字符串类型，通过Body传入，描述为"配置中LLM模型的名称"，用于指定需要获取配置的模型名称。
- `placeholder`: 字符串类型，通过Body传入，描述为"占位用，无实际效果"，此参数在函数内部没有被使用，仅作为API设计时的占位符。

**代码描述**:
`get_model_config`函数首先定义了一个空字典`config`，用于存储过滤后的模型配置项。函数通过调用`get_model_worker_config`函数，传入`model_name`参数，获取指定模型的工作配置项。然后，函数遍历这些配置项，通过一系列条件判断（排除包含"worker_class"、"key"、"secret"或以"id"结尾的键），过滤掉敏感信息或不需要公开的配置项，并将剩余的配置项添加到`config`字典中。

最后，函数返回一个`BaseResponse`对象，其中`data`字段包含了过滤后的模型配置项。这样，调用方可以通过标准的API响应格式，获取到所需的模型配置信息。

**注意**:
- 在使用此函数时，需要确保传入的`model_name`参数正确，且对应的模型配置已经在系统中正确配置，否则可能无法获取到预期的配置信息。
- 此函数通过过滤敏感信息来保护模型配置的安全性，因此返回的配置项中不会包含可能泄露模型内部实现细节的信息。
- 返回的`BaseResponse`对象中的`code`、`msg`字段可以用于判断请求处理的状态和结果，确保调用方可以正确处理响应数据。

**输出示例**:
```python
{
    "code": 200,
    "msg": "success",
    "data": {
        "model_version": "1.0",
        "language": "English",
        // 其他非敏感配置项
    }
}
```
此示例展示了函数调用成功时可能返回的响应格式，其中`data`字段包含了过滤后的模型配置项，而`code`和`msg`字段表示请求处理成功。
## FunctionDef stop_llm_model(model_name, controller_address)
**stop_llm_model**: 此函数的功能是向fastchat controller请求停止某个LLM模型。

**参数**:
- `model_name`: 要停止的LLM模型的名称，此参数是必需的。
- `controller_address`: Fastchat controller服务器的地址，此参数是可选的。如果未提供，则会使用`fschat_controller_address`函数获取默认地址。

**代码描述**:
`stop_llm_model`函数主要用于停止指定的LLM模型。首先，如果没有提供`controller_address`参数，函数会调用`fschat_controller_address`来获取Fastchat控制器的地址。然后，使用`get_httpx_client`函数获取一个httpx客户端实例，通过这个客户端向Fastchat控制器发送POST请求，请求的URL是由控制器地址和`/release_worker`路径组成，请求体中包含了要停止的模型名称。如果请求成功，函数将返回控制器的响应内容。在异常情况下，函数会记录错误信息并返回一个包含错误信息的`BaseResponse`对象。

**注意**:
- 在调用此函数时，确保提供的模型名称是正确且当前正在运行的。如果模型名称错误或模型未运行，可能会导致停止操作失败。
- 如果未能成功连接到Fastchat控制器或控制器处理请求失败，函数会返回一个包含错误信息的`BaseResponse`对象，其中`code`为500，表示服务器内部错误。
- 由于Fastchat的实现方式，停止LLM模型实际上是停止了模型所在的model_worker。

**输出示例**:
假设成功停止了名为"example_model"的LLM模型，函数可能返回如下的`BaseResponse`对象：
```python
{
    "code": 200,
    "msg": "success",
    "data": null
}
```
如果尝试停止一个不存在的模型，或者与Fastchat控制器的通信失败，返回的`BaseResponse`对象可能如下：
```python
{
    "code": 500,
    "msg": "failed to stop LLM model example_model from controller: http://127.0.0.1:8080。错误信息是： ConnectionError",
    "data": null
}
```
## FunctionDef change_llm_model(model_name, new_model_name, controller_address)
**change_llm_model**: 此函数的功能是向fastchat controller请求切换LLM模型。

**参数**:
- `model_name`: 字符串类型，表示当前运行的模型名称。
- `new_model_name`: 字符串类型，表示要切换到的新模型名称。
- `controller_address`: 字符串类型，表示Fastchat controller服务器的地址。如果未提供，则会使用`fschat_controller_address`函数获取默认地址。

**代码描述**:
`change_llm_model`函数首先检查`controller_address`参数是否提供，如果未提供，则调用`fschat_controller_address`函数获取Fastchat controller的地址。然后，使用`get_httpx_client`函数获取一个httpx客户端实例，用于发送HTTP POST请求到controller地址的`/release_worker`端点。请求的JSON体包含`model_name`和`new_model_name`字段，分别表示当前模型和要切换到的新模型。请求超时时间由`HTTPX_DEFAULT_TIMEOUT`常量定义。如果请求成功，函数将返回controller的响应JSON。在遇到异常时，函数会记录错误日志，并返回一个包含错误信息的`BaseResponse`对象。

**注意**:
- 确保`controller_address`正确指向Fastchat controller服务器，否则请求将失败。
- 使用此函数时，应确保`model_name`和`new_model_name`正确且对应的模型在服务器上可用。
- 函数中使用了`get_httpx_client`来获取httpx客户端实例，确保了代理设置和超时配置的正确应用，同时也支持了异常处理和日志记录。

**输出示例**:
成功切换模型时，可能的返回值示例为：
```json
{
  "code": 200,
  "msg": "Model switched successfully",
  "data": {
    "previous_model": "old_model_name",
    "current_model": "new_model_name"
  }
}
```
在遇到错误时，返回值示例为：
```json
{
  "code": 500,
  "msg": "failed to switch LLM model from controller: http://127.0.0.1:8080。错误信息是：ConnectionError"
}
```
## FunctionDef list_search_engines
**list_search_engines**: 此函数的功能是列出服务器支持的搜索引擎。

**参数**: 此函数没有参数。

**代码描述**: `list_search_engines` 函数首先从 `server.chat.search_engine_chat` 模块导入 `SEARCH_ENGINES` 变量，该变量包含了服务器支持的所有搜索引擎的列表。然后，函数使用 `BaseResponse` 类构造一个响应对象，其中 `data` 字段被设置为 `SEARCH_ENGINES` 列表的内容。`BaseResponse` 类是一个标准化的 API 响应格式，包含 `code`、`msg` 和 `data` 三个字段，分别表示 API 的状态码、状态消息和返回的数据内容。在本函数中，只需关注 `data` 字段，它被用来存放搜索引擎列表。

**注意**:
- `list_search_engines` 函数返回的是一个 `BaseResponse` 对象，因此在调用此函数时，应当处理这个对象，以获取其中的数据。
- 由于 `SEARCH_ENGINES` 是从另一个模块导入的，确保该变量在导入前已正确定义和初始化。
- 此函数没有接收任何参数，因此可以直接调用而无需提供额外的信息。

**输出示例**:
调用 `list_search_engines` 函数可能返回的示例响应如下：
```python
{
    "code": 200,
    "msg": "success",
    "data": ["Google", "Bing", "DuckDuckGo"]
}
```
此示例中，`code` 和 `msg` 字段表示请求成功处理，而 `data` 字段包含了一个列表，列出了服务器支持的搜索引擎名称。

## ClassDef ApiRequest
**ApiRequest**: ApiRequest 类的功能是封装 HTTP 请求，简化与 API 服务器的交互过程。

**属性**:
- `base_url`: API 服务器的基础 URL。
- `timeout`: 请求超时时间，默认值由 `HTTPX_DEFAULT_TIMEOUT` 定义。
- `_use_async`: 是否使用异步模式，默认为 False。
- `_client`: 内部使用的 httpx 客户端实例。

**代码描述**:
ApiRequest 类提供了一个简化的方式来与 API 服务器进行交互。它支持 GET、POST 和 DELETE HTTP 方法，并且可以处理同步和异步请求。通过内部管理 httpx 客户端实例，它能够有效地重用连接，提高请求效率。此外，ApiRequest 类还提供了流式请求的支持，以及将响应转换为 JSON 或其他格式的便捷方法。

- `client` 属性负责创建和获取 httpx 客户端实例。如果当前实例未创建或已关闭，它会根据配置重新创建一个。
- `get`、`post` 和 `delete` 方法分别对应 HTTP 的 GET、POST 和 DELETE 请求。这些方法支持重试机制，可以在请求失败时自动重试。
- `_httpx_stream2generator` 方法将 httpx 的流式响应转换为 Python 的生成器，便于处理大量数据。
- `_get_response_value` 方法用于处理响应数据，支持将响应转换为 JSON 或通过自定义函数处理。
- 类还包含了一系列特定功能的方法，如 `get_server_configs`、`list_search_engines`、`get_prompt_template` 等，这些方法封装了与 API 服务器交互的具体细节，使得调用者无需关心请求的构造和响应的解析。

在项目中，ApiRequest 类被多个模块调用，例如 `dialogue_page`、`knowledge_base_page` 和 `model_config_page` 等，用于实现与后端 API 的交互，包括获取服务器配置、执行对话、管理知识库等功能。这些调用展示了 ApiRequest 类在简化 API 调用方面的实际应用。

**注意**:
- 使用 ApiRequest 类时，需要确保 `base_url` 正确指向 API 服务器。
- 在处理异步请求时，需要注意 `_use_async` 属性的设置，以及相应的异步方法调用。

**输出示例**:
假设调用 `get_server_configs` 方法，可能的返回值为：
```json
{
  "code": 200,
  "msg": "成功",
  "data": {
    "server_version": "1.0.0",
    "api_version": "1.0.0"
  }
}
```
此示例展示了一个成功获取服务器配置的响应，其中包含了服务器和 API 的版本信息。
### FunctionDef __init__(self, base_url, timeout)
**__init__**: 此函数的功能是初始化ApiRequest对象。

**参数**:
- `base_url`: 字符串类型，默认值为`api_address()`函数的返回值。用于指定API请求的基础URL。
- `timeout`: 浮点数类型，默认值为`HTTPX_DEFAULT_TIMEOUT`。用于指定请求的超时时间。

**代码描述**: `__init__`函数是`ApiRequest`类的构造函数，负责初始化该类的实例。在初始化过程中，首先设置`base_url`属性，其值默认通过调用`api_address`函数获取，该函数返回API服务器的地址。这一步骤确保了`ApiRequest`对象能够知道向哪个服务器地址发送请求。其次，设置`timeout`属性，用于定义网络请求的超时时间，以避免因网络问题导致程序长时间挂起。此外，函数还初始化了两个内部使用的属性：`_use_async`设置为`False`，表示默认不使用异步请求；`_client`初始化为`None`，预留作为HTTP客户端实例的存储位置。

从功能角度看，`__init__`函数通过提供灵活的初始化参数（如API服务器地址和请求超时时间），使得`ApiRequest`类的实例能够根据不同的需求进行定制化的网络请求。通过调用`api_address`函数获取API服务器地址，`ApiRequest`类与项目中其他部分共享了统一的服务器地址配置，这有助于维护项目的一致性和可配置性。

**注意**: 使用`ApiRequest`类时，需要确保项目配置文件中的API服务器地址（通过`api_address`函数获取）是正确的。此外，考虑到网络请求可能会因各种原因失败，使用`ApiRequest`类进行网络请求时应当做好异常处理。
***
### FunctionDef client(self)
**client**: 此函数的功能是获取或创建一个httpx客户端实例。

**参数**: 此函数不接受任何外部参数。

**代码描述**: `client` 函数首先检查 `_client` 属性是否为 `None` 或者该客户端实例是否已经关闭（通过 `is_closed` 属性判断）。如果满足上述任一条件，函数将通过调用 `get_httpx_client` 函数创建一个新的 httpx 客户端实例，并将其赋值给 `_client` 属性。在创建客户端实例时，会传递几个关键参数给 `get_httpx_client` 函数，包括 `base_url`（基础URL）、`use_async`（是否使用异步客户端）以及 `timeout`（请求超时时间）。这些参数的值来源于 `ApiRequest` 类的属性。如果 `_client` 已经存在且没有关闭，函数将直接返回 `_client`。

**注意**:
- `_client` 是 `ApiRequest` 类的一个私有属性，用于存储 httpx 客户端实例。
- `get_httpx_client` 函数用于创建并配置 httpx 客户端实例，支持同步或异步客户端的创建，具体取决于 `use_async` 参数的值。
- 在多次调用 `client` 函数时，如果已存在一个未关闭的客户端实例，将复用该实例，避免频繁创建新的客户端实例。

**输出示例**: 由于此函数的输出是一个 httpx 客户端实例，输出示例将依赖于如何使用该实例进行 HTTP 请求。例如，使用此客户端实例发起 GET 请求的代码可能如下：
```python
api_request = ApiRequest()  # 假设 ApiRequest 是包含 client 函数的类的实例
httpx_client = api_request.client()
response = httpx_client.get('https://www.example.com')
print(response.text)
```
在这个示例中，首先创建了 `ApiRequest` 类的一个实例 `api_request`，然后通过调用 `client` 函数获取 httpx 客户端实例 `httpx_client`，最后使用该客户端实例发起一个 GET 请求并打印响应内容。
***
### FunctionDef get(self, url, params, retry, stream)
**get**: 此函数的功能是通过HTTP GET请求获取指定URL的数据。

**参数**:
- `url`: 字符串类型，指定请求的URL。
- `params`: 可选参数，字典、列表（包含元组）或字节类型，用于指定请求的查询参数。
- `retry`: 整型，可选参数，默认值为3，指定请求失败时的重试次数。
- `stream`: 布尔类型，可选参数，默认值为False，指定是否以流的形式获取响应内容。
- `**kwargs`: 接收任意额外的关键字参数，这些参数将直接传递给httpx的请求方法。

**代码描述**:
此函数主要用于执行HTTP GET请求。它首先尝试使用`client`方法获取一个httpx客户端实例，然后根据`stream`参数的值决定是调用`client.stream`方法以流的形式获取响应，还是调用`client.get`方法获取完整的响应内容。如果请求过程中发生异常，函数会记录错误信息，并根据`retry`参数的值决定是否重试请求。重试次数`retry`每次异常捕获后减一，直到重试次数用尽。如果在重试次数用尽前请求成功，函数将返回响应内容；否则，可能返回`None`。

**注意**:
- 函数在请求过程中可能会遇到各种异常，例如网络连接问题、服务器错误等。这些异常会被捕获并记录日志，但不会直接抛出，以避免中断程序的执行。
- 通过`**kwargs`参数，用户可以传递额外的选项给httpx请求，如自定义请求头、超时设置等，这提供了高度的灵活性。
- 使用`stream`参数可以在处理大文件或实时数据时减少内存消耗，因为它允许逐块处理响应内容。

**输出示例**:
由于此函数的返回值依赖于请求的响应，因此输出示例将根据调用情境而异。例如，如果请求成功并且不使用流式响应，函数可能返回一个`httpx.Response`对象，可以通过该对象的属性和方法访问响应状态码、响应头、响应内容等信息。如果使用流式响应，函数将返回一个迭代器，允许逐块读取响应内容。
***
### FunctionDef post(self, url, data, json, retry, stream)
**post**: 此函数用于执行HTTP POST请求。

**参数**:
- `url`: 字符串类型，指定请求的URL。
- `data`: 字典类型，默认为None，用于指定要发送的表单数据。
- `json`: 字典类型，默认为None，用于指定要发送的JSON数据。
- `retry`: 整型，默认为3，指定请求失败时的重试次数。
- `stream`: 布尔类型，默认为False，指定是否以流的方式接收响应内容。
- `**kwargs`: 接收任意额外的关键字参数，这些参数将直接传递给httpx的请求方法。

**代码描述**:
此函数首先检查重试次数`retry`是否大于0。如果是，尝试执行POST请求。根据`stream`参数的值，决定是调用httpx客户端的`stream`方法还是`post`方法来发送请求。如果请求过程中发生异常，将捕获异常并记录错误信息，然后重试次数减一，继续尝试发送请求，直到成功或重试次数用尽。异常信息的记录依赖于`logger.error`方法，其中包括异常类型、错误消息和可选的异常信息（取决于`log_verbose`变量的值）。

**注意**:
- 函数内部使用了`self.client`来获取httpx客户端实例，该实例的创建和配置详见`client`函数的文档。
- 当`stream`参数为True时，使用`client.stream`方法以流的方式接收响应，适用于处理大量数据。
- 通过`**kwargs`参数，可以传递额外的参数给httpx的请求方法，如自定义请求头、超时设置等。
- 函数捕获并处理了所有异常，确保了网络请求的健壮性。

**输出示例**:
由于此函数的返回值依赖于请求的响应，因此具体的输出示例将根据不同的请求URL和参数而有所不同。一般情况下，如果不使用流模式，返回值可能是一个`httpx.Response`对象，可以通过该对象访问响应状态码、响应头、响应体等信息。如果使用流模式，返回值可能是一个迭代器，用于逐块处理响应内容。如果请求失败且重试次数用尽，可能返回None。
***
### FunctionDef delete(self, url, data, json, retry, stream)
**delete**: 此函数的功能是通过HTTP DELETE请求删除指定的资源。

**参数**:
- `url`: 字符串类型，指定要删除资源的URL。
- `data`: 字典类型，默认为None，用于指定要发送的数据体。
- `json`: 字典类型，默认为None，用于指定要发送的JSON数据。
- `retry`: 整型，默认为3，指定请求失败时的重试次数。
- `stream`: 布尔类型，默认为False，指定是否以流的形式接收响应数据。
- `**kwargs`: 接收任意额外的关键字参数，这些参数将直接传递给httpx的请求方法。

**代码描述**:
此函数主要用于发送HTTP DELETE请求，以删除指定的资源。它首先会根据`retry`参数指定的次数尝试发送请求。在尝试过程中，如果设置了`stream`参数为True，则会使用`client.stream`方法以流的形式发送DELETE请求；否则，使用`client.delete`方法发送普通的DELETE请求。这里的`client`是通过`ApiRequest`类的`client`方法获取的httpx客户端实例，该实例负责实际的网络通信。在请求过程中，如果遇到异常，会捕获异常并记录错误信息，然后根据`retry`参数决定是否重试。每次重试前，`retry`的值会减1，直到减到0为止。

**注意**:
- 在使用此函数时，需要确保传入的`url`参数是有效的，并且有权限进行DELETE操作。
- 如果服务器响应的内容很大，设置`stream`为True可以减少内存的使用。
- 通过`**kwargs`参数，可以传递额外的请求选项，如自定义头部、超时时间等，以满足不同的请求需求。
- 函数可能返回`httpx.Response`对象、`Iterator[httpx.Response]`对象（当`stream`为True时）或者在重试次数用尽仍失败时返回None。

**输出示例**:
由于此函数的输出依赖于实际的请求和服务器响应，以下是一个可能的返回值示例：
```python
response = api_request.delete('https://www.example.com/resource')
if response:
    print(response.status_code)
else:
    print("请求失败，已重试指定次数。")
```
在这个示例中，首先尝试删除指定URL的资源，然后根据返回值判断请求是否成功。如果请求成功，打印出响应的状态码；如果请求失败且重试次数用尽，则打印失败信息。
***
### FunctionDef _httpx_stream2generator(self, response, as_json)
**_httpx_stream2generator**: 该函数的功能是将httpx.stream返回的GeneratorContextManager转化为普通生成器，以便处理异步或同步的HTTP流响应。

**参数**:
- `response`: contextlib._GeneratorContextManager类型，表示httpx请求的响应流。
- `as_json`: 布尔类型，默认为False，指定是否将流中的数据解析为JSON格式。

**代码描述**:
_httpx_stream2generator函数旨在处理来自httpx库的HTTP流响应。它提供了异步和同步两种处理方式，根据ApiRequest对象的_use_async属性来决定使用哪种方式。当处理异步流时，它使用`async with`语句管理响应上下文，并通过`aiter_text`异步迭代响应内容。对于同步流，使用`with`语句和`iter_text`方法迭代响应内容。无论哪种方式，函数都会检查每个数据块，如果`as_json`参数为True，则尝试将数据块解析为JSON对象；否则，直接返回数据块。

在解析JSON时，函数特别处理了以"data: "开头的数据块，这通常用于服务器发送事件（SSE）。如果数据块以":"开头，则视为SSE的注释行并跳过。如果在解析JSON过程中遇到异常，函数会记录错误信息并继续处理下一个数据块。

此外，函数还处理了几种异常情况，包括无法连接API服务器、API通信超时和其他通信错误，对这些异常情况进行了日志记录，并生成包含错误代码和消息的JSON对象作为生成器的输出。

在项目中，_httpx_stream2generator函数被多个API请求方法调用，如`chat_chat`、`agent_chat`、`knowledge_base_chat`、`file_chat`和`search_engine_chat`等，用于处理这些方法中的流式响应。这些方法通过API与后端服务进行交互，获取实时的数据流。通过使用_httpx_stream2generator函数，这些方法能够以一种统一和高效的方式处理来自后端服务的流式数据。

**注意**:
- 使用此函数时，需要确保传入的response参数是一个有效的httpx的响应流对象。
- 当处理大量数据或需要实时响应时，正确选择异步或同步模式对性能有重要影响。

**输出示例**:
```python
# 如果as_json为True，且流中的数据是JSON格式
{"name": "example", "value": 123}

# 如果as_json为False
"data: example stream data\n"
```
#### FunctionDef ret_async(response, as_json)
**ret_async**: 此函数的功能是异步处理HTTP响应，根据参数决定是否将响应内容作为JSON解析，并以生成器的形式返回数据。

**参数**:
- `response`: 一个异步的HTTP响应对象，此对象应支持异步上下文管理和异步迭代。
- `as_json`: 一个布尔值，指示是否应将响应内容解析为JSON。

**代码描述**:
`ret_async` 函数是一个异步生成器，用于处理来自HTTP请求的响应。它首先尝试异步地与响应对象进行交互。通过迭代响应内容的每个文本块，函数可以根据`as_json`参数的值决定处理方式。

- 当`as_json`为True时，函数尝试将每个块解析为JSON。如果块以`data: `开头，它会去除前缀和后缀后尝试解析JSON；如果块以冒号`:`开头，则视为SSE（Server-Sent Events）注释行并跳过；否则，直接尝试解析整个块为JSON。解析成功后，将解析后的数据作为生成器的下一个值。如果解析失败，会记录错误信息并继续处理下一个块。

- 当`as_json`为False时，直接将文本块作为生成器的下一个值，不进行JSON解析。

函数还处理了几种异常情况，包括连接错误（`httpx.ConnectError`）、读取超时（`httpx.ReadTimeout`）以及其他异常。在遇到这些异常时，会记录相应的错误信息，并生成包含错误代码和消息的字典作为生成器的下一个值。

**注意**:
- 使用此函数时，需要确保传入的`response`对象支持异步操作。
- 函数内部捕获并处理了多种异常，调用者应注意处理生成器可能产生的错误信息字典。
- 由于函数使用了异步特性，调用此函数时需要在异步环境中使用`async for`来获取数据。
- 函数的错误日志依赖于外部的`logger`对象和`log_verbose`变量，需要确保这些依赖在调用环境中正确配置。
***
#### FunctionDef ret_sync(response, as_json)
**ret_sync**: 此函数用于同步处理HTTP响应，并根据需要将响应内容转换为JSON或直接文本。

**参数**:
- `response`: HTTP响应对象，此对象应支持上下文管理协议以及迭代文本内容的方法。
- `as_json`: 布尔值，指示是否应将响应内容解析为JSON。

**代码描述**:
`ret_sync` 函数首先尝试处理传入的HTTP响应。使用`response`对象的上下文管理器确保安全地处理响应。函数迭代响应内容的每个文本块，跳过任何空块，这是为了处理某些API在开始和结束时可能发送的空字节。

如果`as_json`参数为真，函数会尝试将文本块解析为JSON。特别地，如果文本块以"data: "开头，函数会去除这个前缀和最后的两个字符后尝试解析JSON；如果文本块以":"开头，则认为这是一个SSE（Server-Sent Events）的注释行并跳过；否则，直接尝试解析整个文本块为JSON。如果在解析过程中遇到任何异常，会记录错误信息，并根据`log_verbose`变量的值决定是否记录详细的异常信息。

如果`as_json`参数为假，函数则直接将文本块作为迭代器的一部分返回，不进行JSON解析。

函数还处理了几种特定的异常情况，包括连接错误（`httpx.ConnectError`）、读取超时（`httpx.ReadTimeout`）以及其他异常。在这些情况下，会记录相应的错误信息，并通过迭代器返回包含错误代码和消息的字典。

**注意**:
- 使用此函数时，需要确保传入的`response`对象支持所需的操作，包括上下文管理和文本迭代。
- 当选择以JSON格式解析响应时，应注意处理可能的解析错误，并准备好接收错误信息。
- 异常处理部分显示了如何处理特定的连接和超时错误，这对于调试和错误处理非常有用。
- 此函数的设计考虑了SSE（Server-Sent Events）格式的响应，这在实时数据传输中非常常见。
***
***
### FunctionDef _get_response_value(self, response, as_json, value_func)
**_get_response_value**: 此函数的功能是转换HTTP响应对象，根据指定的参数返回处理后的数据。

**参数**:
- `response`: httpx.Response对象，代表一个HTTP响应。
- `as_json`: 布尔值，默认为False。当设置为True时，函数会尝试将响应体解析为JSON。
- `value_func`: 可调用对象，默认为None。用户可以通过此参数传入一个函数，该函数接收一个参数（响应体或其JSON解析结果），并返回处理后的数据。

**代码描述**:
此函数主要用于处理API请求的响应数据。它提供了灵活的处理方式，支持直接返回响应体、返回响应体的JSON解析结果，或通过`value_func`参数自定义处理逻辑。函数内部首先定义了一个`to_json`的内部函数，用于尝试将响应体解析为JSON，如果解析失败，则记录错误信息并返回一个包含错误代码和信息的字典。接着，根据`_use_async`属性判断当前是否使用异步模式，并据此选择同步或异步的处理方式。如果`as_json`参数为True，则使用`to_json`函数处理响应体；如果用户通过`value_func`参数提供了自定义处理函数，则最终返回的数据会经过该函数处理。

在项目中，`_get_response_value`函数被多个API请求函数调用，用于处理这些函数获取的HTTP响应。例如，在获取服务器配置、列出搜索引擎、获取提示模板等场景中，都使用了此函数来处理响应数据，并根据需要将响应解析为JSON或通过自定义函数进一步处理。这种设计使得响应数据的处理更加灵活和统一。

**注意**:
- 当使用`as_json`参数时，需要确保响应体可以被成功解析为JSON，否则会返回错误信息。
- 如果提供了`value_func`参数，需要确保传入的函数能够正确处理输入的数据（响应体或其JSON解析结果），并返回期望的结果。

**输出示例**:
假设响应体为`{"code": 200, "msg": "成功", "data": {"key": "value"}}`，并且`as_json`参数为True，没有提供`value_func`参数，则函数的返回值可能为：
```python
{"code": 200, "msg": "成功", "data": {"key": "value"}}
```
#### FunctionDef to_json(r)
**to_json**: 该函数的功能是将响应对象转换为JSON格式。

**参数**:
- r: 需要被转换为JSON格式的响应对象。

**代码描述**:
`to_json`函数旨在处理API响应，尝试将响应对象`r`转换为JSON格式。这个过程中，函数首先尝试使用`r.json()`方法来解析响应内容。如果在解析过程中遇到任何异常（例如，响应内容不是有效的JSON格式），则会捕获这个异常，并构造一个包含错误代码500、错误消息以及空数据的JSON对象返回。错误消息会附加异常信息，以便于调试和错误追踪。如果启用了详细日志（`log_verbose`为真），则会记录错误信息和异常类型到日志中，以供后续分析。

在项目中，`to_json`函数被`ret_async`函数调用，用于异步处理API响应。在`ret_async`中，根据`as_json`参数的值决定是否需要将响应转换为JSON。如果需要，`ret_async`会使用`to_json`函数处理经过`await`获取的响应对象，然后将转换后的JSON数据传递给`value_func`函数进行进一步处理。这表明`to_json`函数在处理异步API响应中起到了关键的数据格式转换作用。

**注意**:
- 在使用`to_json`函数时，需要确保传入的响应对象具有`.json()`方法，这通常意味着该对象是一个HTTP响应对象。
- 函数内部捕获的异常是广泛的，因此在调用此函数时，应当注意异常处理，以避免隐藏潜在的错误。

**输出示例**:
如果响应内容是有效的JSON，例如`{"name": "test"}`，则`to_json`函数将返回这个JSON对象。
如果响应内容不是有效的JSON，假设发生了一个解析异常，函数可能返回如下格式的JSON对象：
```json
{
  "code": 500,
  "msg": "API未能返回正确的JSON。解析错误信息",
  "data": None
}
```
***
#### FunctionDef ret_async(response)
**ret_async**: 该函数的功能是异步处理API响应，并根据需要将其转换为JSON格式或直接返回。

**参数**:
- response: 需要被处理的异步响应对象。

**代码描述**:
`ret_async`函数是设计用来异步处理API响应的。它接受一个`response`参数，这是一个异步响应对象。函数内部首先判断是否需要将响应转换为JSON格式，这是通过检查`as_json`变量的值来决定的。如果`as_json`为真，则调用`to_json`函数将响应转换为JSON格式；否则，直接返回响应内容。

在转换为JSON格式的过程中，`ret_async`函数使用`await`关键字等待`response`对象的异步操作完成，然后将结果传递给`to_json`函数进行处理。处理完成后，将转换后的JSON数据传递给`value_func`函数进行进一步处理。

如果不需要将响应转换为JSON格式，`ret_async`函数同样使用`await`关键字等待响应内容的异步操作完成，然后直接将结果传递给`value_func`函数。

这个函数展示了异步编程在处理API响应时的应用，特别是在需要对响应数据进行格式转换或其他处理时的灵活性。

**注意**:
- 在调用`ret_async`函数时，需要确保传入的`response`对象支持异步操作。
- `as_json`变量和`value_func`函数在代码片段中未显示定义，需要在`ret_async`函数被调用的上下文中提供。
- `to_json`函数的作用是将响应对象转换为JSON格式，因此在`as_json`为真时，需要确保响应对象能够被成功转换。

**输出示例**:
- 如果`as_json`为真，并且响应内容是有效的JSON，例如`{"name": "test"}`，`ret_async`函数可能返回经过`value_func`处理的JSON对象。
- 如果`as_json`为假，假设响应内容是字符串"response content"，`ret_async`函数将返回经过`value_func`处理的字符串"response content"。
***
***
### FunctionDef get_server_configs(self)
**get_server_configs**: 此函数用于获取服务器配置信息。

**参数**:
- `**kwargs`: 可变关键字参数，允许传递任意数量的参数名及其对应的值，这些参数将直接传递给内部的`post`方法。

**代码描述**:
`get_server_configs`函数通过调用`post`方法向服务器发送HTTP POST请求，请求的URL为`"/server/configs"`。该函数接受任意数量的关键字参数(`**kwargs`)，这些参数将直接传递给`post`方法。在发送请求后，函数通过调用`_get_response_value`方法处理响应，将响应体转换为JSON格式的字典并返回。`_get_response_value`方法支持将响应体解析为JSON，并且可以通过传入的参数自定义处理逻辑，以满足不同的数据处理需求。

**注意**:
- 使用此函数时，可以通过`**kwargs`传递额外的参数给`post`方法，例如自定义请求头、超时设置等，这提供了灵活的请求配置能力。
- 函数依赖于`post`方法来发送HTTP请求，因此其性能和异常处理能力与`post`方法的实现紧密相关。
- 返回的数据格式为JSON，调用方应确保处理JSON格式的数据。

**输出示例**:
调用`get_server_configs`函数可能返回的示例数据如下：
```python
{
    "code": 200,
    "msg": "成功",
    "data": {
        "config1": "value1",
        "config2": "value2",
        // 更多配置项...
    }
}
```
此示例展示了一个包含状态码、消息和数据的标准响应结构，其中`data`字段包含了服务器配置的详细信息。实际返回的数据结构可能根据服务器的不同配置而有所不同。
***
### FunctionDef list_search_engines(self)
**list_search_engines**: 此函数用于列出可用的搜索引擎列表。

**参数**:
- `**kwargs`: 接收任意额外的关键字参数，这些参数将直接传递给内部的POST请求方法。

**代码描述**:
`list_search_engines` 函数通过发送一个HTTP POST请求到`/server/list_search_engines`路径，获取可用的搜索引擎列表。它使用了`post`方法来执行这个请求，并且可以接受任意额外的关键字参数（`**kwargs`），这些参数将直接传递给`post`方法。在获取到响应后，函数使用`_get_response_value`方法来处理响应数据，这个处理包括将响应体解析为JSON格式，并从中提取`data`字段的值作为最终的返回结果。

**注意**:
- 函数内部依赖于`post`方法来发送HTTP请求，因此确保`post`方法能够正确执行是使用此函数的前提。
- 函数还依赖于`_get_response_value`方法来处理响应数据，确保该方法能正确解析响应体并提取所需数据。
- 由于此函数可以接受任意额外的关键字参数，这提供了一定的灵活性，例如可以通过这些参数来定制HTTP请求头或设置超时等。

**输出示例**:
假设服务器端返回的响应体为`{"code": 200, "msg": "成功", "data": ["Google", "Bing", "DuckDuckGo"]}`，则`list_search_engines`函数的返回值将是一个列表，如下所示：
```python
["Google", "Bing", "DuckDuckGo"]
```
这个列表包含了所有可用的搜索引擎名称。
***
### FunctionDef get_prompt_template(self, type, name)
**get_prompt_template**: 此函数用于获取指定类型和名称的提示模板。

**参数**:
- `type`: 字符串类型，默认值为"llm_chat"，用于指定请求的提示模板类型。
- `name`: 字符串类型，默认值为"default"，用于指定请求的提示模板名称。
- `**kwargs`: 接收任意额外的关键字参数，这些参数将直接传递给内部的`post`方法。

**代码描述**:
`get_prompt_template`函数首先构造一个包含`type`和`name`的字典`data`，然后使用`post`方法向服务器发送请求，请求的URL为`/server/get_prompt_template`，并且将`data`字典作为JSON数据传递。此外，任何通过`**kwargs`传递的额外参数也会被直接传递给`post`方法。接收到的响应通过`_get_response_value`方法处理，该方法允许通过`value_func`参数自定义响应值的处理逻辑。在本函数中，`value_func`被设置为一个lambda函数，该函数接收响应对象并返回其文本内容。因此，`get_prompt_template`函数最终返回的是服务器响应的文本内容。

**注意**:
- 函数内部通过`post`方法发送HTTP POST请求，因此需要确保网络连接的稳定性。
- `_get_response_value`方法用于处理响应数据，可以根据需要自定义处理逻辑，但在本函数中仅返回响应的文本内容。
- 通过`**kwargs`参数，可以向`post`方法传递额外的请求参数，如自定义请求头、超时设置等，增加了函数的灵活性。

**输出示例**:
假设服务器对于请求的提示模板返回了文本内容`"Welcome to the chat!"`，则函数的返回值可能为：
```
"Welcome to the chat!"
```
此输出示例展示了函数在成功获取提示模板时可能返回的文本内容。实际返回的内容将根据服务器的响应而有所不同。
***
### FunctionDef chat_chat(self, query, conversation_id, history_len, history, stream, model, temperature, max_tokens, prompt_name)
**chat_chat**: 该函数用于处理与聊天相关的API请求。

**参数**:
- `query`: 字符串类型，用户的查询内容。
- `conversation_id`: 字符串类型，默认为None，表示会话的唯一标识符。
- `history_len`: 整型，默认为-1，表示需要考虑的历史消息数量。
- `history`: 列表类型，默认为空列表，包含历史对话内容的列表，每个元素是一个字典。
- `stream`: 布尔类型，默认为True，指定是否以流的方式接收响应内容。
- `model`: 字符串类型，默认为LLM_MODELS列表的第一个元素，指定使用的语言模型。
- `temperature`: 浮点类型，默认为TEMPERATURE，控制生成文本的创造性。
- `max_tokens`: 整型，可选参数，默认为None，指定生成文本的最大令牌数。
- `prompt_name`: 字符串类型，默认为"default"，指定使用的提示模板名称。
- `**kwargs`: 接收任意额外的关键字参数。

**代码描述**:
函数首先构造一个包含请求所需所有参数的字典`data`，然后使用`self.post`方法向"/chat/chat"路径发送POST请求，请求体为`data`字典。请求时，`stream`参数被设置为True，表示以流的方式接收响应内容。最后，函数调用`self._httpx_stream2generator`方法，将httpx库返回的流响应转换为普通生成器，并指定以JSON格式解析流中的数据，最终返回该生成器。

**注意**:
- 函数内部调用了`post`方法发送HTTP POST请求，该方法的详细描述可参考`post`函数的文档。
- 函数还调用了`_httpx_stream2generator`方法来处理流式响应，该方法的详细描述可参考`_httpx_stream2generator`函数的文档。
- 通过`**kwargs`参数，可以向`post`方法传递额外的HTTP请求参数，例如自定义请求头或超时设置等。
- 函数设计为支持流式响应，适用于处理实时数据或大量数据的场景。

**输出示例**:
由于函数返回的是一个生成器，具体的输出取决于响应内容。以下是一个可能的输出示例，假设流中的数据是JSON格式：
```python
{
    "text": "这是由模型生成的回答。",
    "message_id": "123456789"
}
```
在实际使用中，生成器将逐步产生此类JSON对象，每个对象包含模型生成的文本和消息ID等信息。
***
### FunctionDef agent_chat(self, query, history, stream, model, temperature, max_tokens, prompt_name)
**agent_chat**: 该函数用于处理代理聊天的请求，并将查询发送到后端服务。

**参数**:
- `query`: 字符串类型，用户的查询内容。
- `history`: 列表类型，默认为空列表，包含字典类型的元素，用于传递对话历史。
- `stream`: 布尔类型，默认为True，指定是否以流的方式接收响应内容。
- `model`: 字符串类型，默认为`LLM_MODELS`列表的第一个元素，用于指定处理请求的模型。
- `temperature`: 浮点类型，默认为`TEMPERATURE`，用于控制生成文本的多样性。
- `max_tokens`: 整型，可选参数，用于指定生成文本的最大令牌数。
- `prompt_name`: 字符串类型，默认为"default"，用于指定使用的提示模板名称。

**代码描述**:
`agent_chat`函数首先构造一个包含请求参数的字典`data`，然后使用`self.post`方法发送POST请求到`/chat/agent_chat`端点。该请求以流的方式接收响应内容。函数最后调用`_httpx_stream2generator`方法，将httpx的流响应转换为普通生成器，以便于处理异步或同步的HTTP流响应，并将其作为返回值。

**注意**:
- 该函数依赖于`post`方法来发送HTTP POST请求，`post`方法的详细行为请参考`post`函数的文档。
- `agent_chat`函数的返回值是一个生成器，它允许调用者以流式方式处理来自后端服务的响应数据。这对于处理大量数据或需要实时响应的场景特别有用。
- 函数中使用了`LLM_MODELS`和`TEMPERATURE`这两个全局变量，它们需要在函数外部定义。

**输出示例**:
由于`agent_chat`函数返回的是一个生成器，其具体输出取决于后端服务的响应内容。假设后端服务返回的数据是JSON格式，且`as_json`参数为True，则可能的输出示例为：
```python
{
    "answer": "这是一个示例回答。",
    "confidence": 0.95
}
```
如果`as_json`参数为False，则可能直接输出后端服务返回的原始文本数据。
***
### FunctionDef knowledge_base_chat(self, query, knowledge_base_name, top_k, score_threshold, history, stream, model, temperature, max_tokens, prompt_name)
**knowledge_base_chat**: 该函数用于通过知识库进行聊天对话。

**参数**:
- `query`: 字符串类型，用户的查询语句。
- `knowledge_base_name`: 字符串类型，指定要查询的知识库名称。
- `top_k`: 整型，默认值为VECTOR_SEARCH_TOP_K，指定返回的相关知识条目数量上限。
- `score_threshold`: 浮点型，默认值为SCORE_THRESHOLD，设置返回知识条目的分数阈值。
- `history`: 列表类型，默认为空列表，包含字典类型的历史对话记录。
- `stream`: 布尔类型，默认为True，指定是否以流的方式接收响应内容。
- `model`: 字符串类型，默认为LLM_MODELS列表的第一个元素，指定使用的语言模型。
- `temperature`: 浮点型，默认值为TEMPERATURE，控制生成文本的多样性。
- `max_tokens`: 整型，可选参数，指定生成文本的最大令牌数。
- `prompt_name`: 字符串类型，默认为"default"，指定使用的提示模板名称。

**代码描述**:
函数首先构造一个包含所有输入参数的字典`data`，然后使用`self.post`方法向`/chat/knowledge_base_chat`路径发送POST请求，并将`data`作为JSON数据传递。请求的响应以流的形式接收，并通过调用`self._httpx_stream2generator`方法将httpx的响应流转换为普通生成器，以便于处理异步或同步的HTTP流响应。该方法返回一个生成器，可以迭代获取处理后的响应数据。

**注意**:
- 函数内部调用了`self.post`方法来发送HTTP POST请求，该方法的详细行为请参考`post`函数的文档。
- 通过`self._httpx_stream2generator`方法处理响应流，该方法的详细行为请参考`_httpx_stream2generator`函数的文档。
- 函数的行为受到传入参数的影响，特别是`stream`参数决定了响应内容的接收方式。
- 使用该函数时，需要确保`knowledge_base_name`参数指定的知识库已经存在并可用。

**输出示例**:
由于该函数返回一个生成器，因此输出示例将依赖于具体的响应内容。假设响应内容为JSON格式的数据，一个可能的输出示例为：
```python
{
    "answer": "这是根据您的查询从知识库中检索到的答案。",
    "docs": [
        {"title": "文档1", "content": "文档1的内容", "score": 0.95},
        {"title": "文档2", "content": "文档2的内容", "score": 0.90}
    ]
}
```
在实际使用中，生成器将逐步产生上述格式的数据块，直到所有相关的响应数据被处理完毕。
***
### FunctionDef upload_temp_docs(self, files, knowledge_id, chunk_size, chunk_overlap, zh_title_enhance)
**upload_temp_docs**: 此函数用于上传临时文档到知识库。

**参数**:
- `files`: 文件列表，可以是字符串、路径或字节数据的列表。
- `knowledge_id`: 字符串类型，指定知识库的ID，默认为None。
- `chunk_size`: 整型，指定分块上传时每个块的大小，默认值由`CHUNK_SIZE`常量决定。
- `chunk_overlap`: 整型，指定分块上传时块之间的重叠大小，默认值由`OVERLAP_SIZE`常量决定。
- `zh_title_enhance`: 布尔值，指定是否增强中文标题，默认值由`ZH_TITLE_ENHANCE`常量决定。

**代码描述**:
此函数首先定义了一个内部函数`convert_file`，用于将输入的文件转换为适合上传的格式。如果文件是字节数据，则将其封装在`BytesIO`对象中；如果文件是可读对象，则直接使用；如果文件是路径，则打开文件并读取为二进制数据。之后，将所有文件通过`convert_file`函数转换，并构造上传数据的字典，包括知识库ID、分块大小、块重叠大小和中文标题增强选项。最后，使用`post`方法向`/knowledge_base/upload_temp_docs`路径发送POST请求，上传文件，并通过`_get_response_value`方法处理响应，返回JSON格式的响应数据。

此函数与`post`和`_get_response_value`方法紧密相关。`post`方法负责执行HTTP POST请求，发送文件和数据到服务器；`_get_response_value`方法则用于处理服务器的响应，将其转换为JSON格式或其他用户定义的格式。这种设计实现了功能的模块化，使得上传文件的过程清晰且易于管理。

**注意**:
- 确保传入的`files`参数中的文件路径存在或文件数据有效，以避免在上传过程中出现错误。
- `chunk_size`和`chunk_overlap`参数应根据服务器的接受能力和网络条件合理设置，以优化上传性能。
- 函数依赖于`post`方法的实现，确保`post`方法能够正确处理文件上传的请求。
- 使用`_get_response_value`处理响应时，确保服务器的响应可以被正确解析为JSON格式。

**输出示例**:
假设上传成功，服务器响应如下JSON数据：
```python
{
    "code": 200,
    "msg": "上传成功",
    "data": {
        "file_ids": ["file1_id", "file2_id"]
    }
}
```
此时，`upload_temp_docs`函数的返回值可能为：
```python
{
    "code": 200,
    "msg": "上传成功",
    "data": {
        "file_ids": ["file1_id", "file2_id"]
    }
}
```
#### FunctionDef convert_file(file, filename)
**convert_file**: 此函数的功能是将传入的文件转换为文件名和文件对象的形式。

**参数**:
- **file**: 可以是字节串、具有read方法的文件对象或本地文件路径。
- **filename**: 可选参数，用于指定文件名。如果未提供，则会根据文件对象或路径自动确定文件名。

**代码描述**:
此函数首先检查`file`参数的类型，以确定其是字节串、文件对象还是文件路径，并据此进行相应的处理：
- 如果`file`是字节串（`bytes`类型），则使用`BytesIO`将其转换为文件对象。
- 如果`file`具有`read`方法（即，它是一个文件对象），则直接使用该对象。如果`filename`参数未提供，将尝试从文件对象的`name`属性获取文件名。
- 如果`file`既不是字节串也没有`read`方法，则假定它是一个本地文件路径。函数将尝试打开该路径指向的文件（以二进制读取模式），并根据需要设置文件名。

在处理完毕后，函数返回一个包含文件名和文件对象的元组。

**注意**:
- 确保传入的文件路径是有效的，否则在尝试打开文件时会引发异常。
- 如果传入的是文件对象，确保它已经以适当的模式（如二进制读取模式）打开。

**输出示例**:
假设有一个位于`/path/to/document.pdf`的文件，调用`convert_file('/path/to/document.pdf')`将返回：
```
('document.pdf', <_io.BufferedReader name='/path/to/document.pdf'>)
```
如果传入的是字节串，假设不提供文件名，调用`convert_file(b'some binary data')`可能返回：
```
(None, <_io.BytesIO object at 0x7f4c3b2f1e50>)
```
请注意，由于字节串没有显式的文件名，所以在这种情况下文件名可能为`None`或者是根据上下文在函数外部指定的。
***
***
### FunctionDef file_chat(self, query, knowledge_id, top_k, score_threshold, history, stream, model, temperature, max_tokens, prompt_name)
**file_chat**: 该函数用于处理文件对话请求，通过发送查询到后端并接收处理结果。

**参数**:
- `query`: 字符串类型，用户的查询内容。
- `knowledge_id`: 字符串类型，指定知识文件的唯一标识符。
- `top_k`: 整型，默认值为`VECTOR_SEARCH_TOP_K`，指定返回的最相关结果的数量。
- `score_threshold`: 浮点型，默认值为`SCORE_THRESHOLD`，指定返回结果的分数阈值。
- `history`: 列表类型，默认为空列表，包含字典类型的历史对话记录。
- `stream`: 布尔类型，默认为True，指定是否以流的方式接收响应内容。
- `model`: 字符串类型，默认为`LLM_MODELS[0]`，指定使用的语言模型。
- `temperature`: 浮点型，默认为`TEMPERATURE`，控制生成文本的创新性。
- `max_tokens`: 整型，可选参数，指定生成文本的最大令牌数。
- `prompt_name`: 字符串类型，默认为"default"，指定使用的提示模板名称。

**代码描述**:
`file_chat`函数首先构造一个包含所有必要信息的数据字典，然后使用`self.post`方法向`/chat/file_chat`端点发送POST请求，并将数据字典作为JSON数据传递。请求以流的方式发送，以便处理可能的大量数据。函数接收到的响应通过`self._httpx_stream2generator`方法转换为生成器，以便于异步处理响应数据。该方法允许以JSON格式逐块处理响应内容，适用于实时数据流的场景。

**注意**:
- 在使用`file_chat`函数时，需要确保`knowledge_id`正确指向了一个有效的知识文件标识符。
- `history`参数允许传递历史对话记录，这有助于模型更好地理解上下文，从而生成更准确的回复。
- 通过调整`top_k`和`score_threshold`参数，可以控制返回结果的数量和质量。
- `stream`参数默认为True，这意味着响应以流的方式处理，适合大数据量的场景。

**输出示例**:
由于`file_chat`函数的输出是通过`self._httpx_stream2generator`方法处理的生成器，因此具体的输出示例将依赖于后端服务的响应。一般情况下，可能会得到类似以下格式的JSON数据流：
```json
{
  "answer": "这是根据您的查询和提供的文件内容生成的回答。",
  "docs": [
    {
      "title": "相关文档1",
      "content": "文档内容摘要。",
      "score": 0.95
    },
    {
      "title": "相关文档2",
      "content": "文档内容摘要。",
      "score": 0.90
    }
  ]
}
```
这个示例展示了一个可能的回答以及与查询最相关的文档列表和它们的匹配分数。
***
### FunctionDef search_engine_chat(self, query, search_engine_name, top_k, history, stream, model, temperature, max_tokens, prompt_name, split_result)
**search_engine_chat**: 此函数用于通过搜索引擎进行聊天式搜索。

**参数**:
- `query`: 字符串类型，用户的查询语句。
- `search_engine_name`: 字符串类型，指定使用的搜索引擎名称。
- `top_k`: 整型，默认为`SEARCH_ENGINE_TOP_K`，指定返回的搜索结果数量。
- `history`: 列表类型，默认为空列表，包含字典类型的元素，用于传递对话历史。
- `stream`: 布尔类型，默认为True，指定是否以流的方式接收响应内容。
- `model`: 字符串类型，默认为`LLM_MODELS[0]`，指定使用的语言模型。
- `temperature`: 浮点类型，默认为`TEMPERATURE`，用于调整生成文本的随机性。
- `max_tokens`: 整型，可选参数，指定生成文本的最大令牌数。
- `prompt_name`: 字符串类型，默认为"default"，用于指定使用的提示模板名称。
- `split_result`: 布尔类型，默认为False，指定是否分割返回的结果。

**代码描述**:
此函数首先构造一个包含所有输入参数的字典`data`，然后使用`self.post`方法向`/chat/search_engine_chat`路径发送POST请求，并传递`data`作为请求体。请求的响应以流的方式接收，并通过`self._httpx_stream2generator`方法转换为普通生成器，以便于处理异步或同步的HTTP流响应。这使得函数能够处理实时数据流，并根据需要将数据块解析为JSON格式或直接返回。

**注意**:
- 函数依赖于`self.post`方法来发送HTTP POST请求，该方法的具体实现和行为可能会影响`search_engine_chat`函数的行为和性能。
- 使用`stream=True`参数调用`self.post`方法，意味着响应内容将以流的方式接收，适用于处理大量数据或实时数据流。
- `self._httpx_stream2generator`方法用于处理httpx库返回的HTTP流响应，根据`as_json=True`参数，将流中的数据解析为JSON格式。

**输出示例**:
假设搜索引擎返回了关于查询“Python编程”的两条结果，函数可能返回如下格式的生成器输出：
```python
[
    {"title": "Python官方文档", "url": "https://docs.python.org", "snippet": "Python官方文档提供了详细的语言参考..."},
    {"title": "Python教程", "url": "https://www.learnpython.org", "snippet": "这个Python教程适合所有级别的编程者..."}
]
```
此输出示例展示了以JSON格式返回的搜索结果，包含每个结果的标题、URL和摘要信息。实际输出将根据搜索引擎的响应和处理逻辑而有所不同。
***
### FunctionDef list_knowledge_bases(self)
**list_knowledge_bases**: 此函数的功能是列出所有可用的知识库。

**参数**: 此函数没有参数。

**代码描述**: `list_knowledge_bases` 函数通过发送 HTTP GET 请求到 `/knowledge_base/list_knowledge_bases` 路径，来获取所有可用的知识库列表。函数首先调用 `get` 方法发送请求，并接收返回的响应。然后，它使用 `_get_response_value` 方法处理这个响应，将响应体解析为 JSON 格式，并从中提取 `data` 字段的值。如果 `data` 字段不存在，则默认返回一个空列表。这个过程使得函数能够以结构化的方式返回知识库列表，便于后续的处理和使用。

**注意**:
- 函数依赖于 `get` 方法来发送 HTTP 请求，因此需要确保网络连接正常，且目标服务器能够响应 `/knowledge_base/list_knowledge_bases` 路径的请求。
- 函数返回的知识库列表以 JSON 格式提供，这要求调用方能够处理 JSON 格式的数据。
- 在处理服务器响应时，如果响应体不能被成功解析为 JSON，或者 `data` 字段不存在，函数将返回一个空列表，而不是抛出异常。这意味着调用方需要对返回的列表进行检查，以确认是否成功获取了知识库列表。

**输出示例**:
假设服务器成功响应并返回了两个知识库的信息，函数可能返回如下格式的数据：
```python
[
    {"id": "kb1", "name": "知识库1", "description": "这是第一个知识库的描述"},
    {"id": "kb2", "name": "知识库2", "description": "这是第二个知识库的描述"}
]
```
如果服务器没有返回任何知识库信息，或者请求失败，函数将返回一个空列表：
```python
[]
```
***
### FunctionDef create_knowledge_base(self, knowledge_base_name, vector_store_type, embed_model)
**create_knowledge_base**: 此函数用于创建一个新的知识库。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要创建的知识库的名称。
- `vector_store_type`: 字符串类型，默认为`DEFAULT_VS_TYPE`，指定向量存储的类型。
- `embed_model`: 字符串类型，默认为`EMBEDDING_MODEL`，指定用于嵌入的模型。

**代码描述**:
`create_knowledge_base`函数主要负责通过API接口创建一个新的知识库。函数首先构造一个包含知识库名称、向量存储类型和嵌入模型的数据字典。然后，使用`post`方法向`/knowledge_base/create_knowledge_base`路径发送POST请求，请求体为上述数据字典。最后，通过调用`_get_response_value`方法处理响应，如果指定`as_json=True`，则尝试将响应体解析为JSON格式并返回。

**注意**:
- 确保传入的`knowledge_base_name`不为空，且为唯一的知识库名称，以避免创建重复的知识库。
- `vector_store_type`和`embed_model`参数应根据实际需求选择合适的类型和模型，这将影响知识库的性能和效果。
- 函数依赖于`post`方法来发送HTTP请求，该方法提供了重试机制和异常处理，确保网络请求的稳定性。
- 函数的返回值取决于API的响应结果，通常包含操作的状态码和消息，可能还包含创建的知识库的详细信息。

**输出示例**:
假设成功创建了一个名为"ExampleKB"的知识库，且使用默认的向量存储类型和嵌入模型，函数可能返回如下JSON格式的数据：
```python
{
    "code": 200,
    "msg": "已新增知识库 ExampleKB",
    "data": {
        "knowledge_base_name": "ExampleKB",
        "vector_store_type": "DEFAULT_VS_TYPE",
        "embed_model": "EMBEDDING_MODEL"
    }
}
```
如果尝试创建一个已存在的知识库名称，可能返回的数据如下：
```python
{
    "code": 404,
    "msg": "已存在同名知识库 ExampleKB"
}
```
***
### FunctionDef delete_knowledge_base(self, knowledge_base_name)
**delete_knowledge_base**: 此函数用于删除指定的知识库。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要删除的知识库名称。

**代码描述**:
`delete_knowledge_base` 函数通过发送HTTP POST请求到`/knowledge_base/delete_knowledge_base`端点，请求删除指定名称的知识库。函数接收一个参数`knowledge_base_name`，该参数指定了要删除的知识库的名称。在发送请求时，该名称作为JSON数据体的一部分被发送。请求的响应通过调用`_get_response_value`函数处理，以确保以JSON格式正确解析响应内容。如果响应成功，该函数将返回解析后的JSON数据。

**注意**:
- 确保传入的`knowledge_base_name`确实存在于系统中，否则可能会导致删除失败。
- 删除知识库是一个不可逆的操作，一旦执行，知识库中的所有数据将被永久删除。
- 在调用此函数之前，建议进行适当的确认流程，以防止意外删除重要数据。

**输出示例**:
假设成功删除名为`example_kb`的知识库，函数可能返回如下JSON格式的数据：
```python
{
    "code": 200,
    "msg": "成功",
    "data": None
}
```
此输出表示请求已成功处理，知识库已被删除。`code`字段表示操作的状态码，200代表成功。`msg`字段提供了关于操作的简短描述。`data`字段在此操作中通常为空，因为删除操作不返回额外数据。
***
### FunctionDef list_kb_docs(self, knowledge_base_name)
**list_kb_docs**: 此函数的功能是列出指定知识库中的文件列表。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要查询的知识库名称。

**代码描述**:
`list_kb_docs`函数通过调用`get`方法，向`/knowledge_base/list_files`端点发送HTTP GET请求，以获取指定知识库的文件列表。请求时，将`knowledge_base_name`作为查询参数传递。接收到响应后，利用`_get_response_value`方法处理响应数据，该方法支持将响应体解析为JSON格式，并通过`value_func`参数提供的函数进一步处理解析后的数据，最终返回一个包含文件列表的数组。

**注意**:
- 确保传入的`knowledge_base_name`参数正确，以便能够查询到正确的知识库文件列表。
- 此函数依赖于`get`和`_get_response_value`方法，确保这些依赖方法能够正常工作。
- 函数处理的响应数据格式依赖于后端API的设计，确保后端`/knowledge_base/list_files`端点的响应格式与此函数的处理逻辑相匹配。

**输出示例**:
假设知识库中存在文件`["document1.pdf", "document2.pdf"]`，则函数可能返回如下数组：
```python
["document1.pdf", "document2.pdf"]
```
此输出示例展示了函数调用成功时，返回的文件列表数组。实际返回的数据将根据指定知识库中实际包含的文件而有所不同。
***
### FunctionDef search_kb_docs(self, knowledge_base_name, query, top_k, score_threshold, file_name, metadata)
**search_kb_docs**: 此函数用于在知识库中搜索文档。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要搜索的知识库名称。
- `query`: 字符串类型，默认为空字符串，指定搜索查询的内容。
- `top_k`: 整型，默认为`VECTOR_SEARCH_TOP_K`，指定返回的最大文档数量。
- `score_threshold`: 整型，默认为`SCORE_THRESHOLD`，指定搜索结果的分数阈值。
- `file_name`: 字符串类型，默认为空字符串，指定要搜索的文件名。
- `metadata`: 字典类型，默认为空字典，指定要搜索的元数据。

**代码描述**:
此函数首先构造一个包含搜索参数的字典`data`，然后使用`post`方法向`/knowledge_base/search_docs`路径发送POST请求，请求体为`data`字典。请求成功后，使用`_get_response_value`方法处理响应，将响应内容解析为JSON格式并返回。这个过程涉及到与后端API的交互，用于在指定的知识库中根据给定的查询条件搜索文档。

**注意**:
- 函数内部调用了`post`方法来执行HTTP POST请求，该方法的详细行为请参考`post`函数的文档。
- 函数还调用了`_get_response_value`方法来处理HTTP响应，该方法的详细行为请参考`_get_response_value`函数的文档。
- 在使用此函数时，需要确保`knowledge_base_name`正确指向一个存在的知识库，且该知识库中有符合搜索条件的文档。
- `top_k`和`score_threshold`参数可以用来调整搜索结果的数量和质量，根据实际需求进行设置。

**输出示例**:
假设搜索查询返回了两个文档，函数的返回值可能如下：
```python
[
    {
        "doc_id": "123",
        "title": "文档标题1",
        "content": "文档内容示例1",
        "score": 0.95,
        "metadata": {"author": "作者1", "date": "2023-01-01"}
    },
    {
        "doc_id": "456",
        "title": "文档标题2",
        "content": "文档内容示例2",
        "score": 0.90,
        "metadata": {"author": "作者2", "date": "2023-02-01"}
    }
]
```
此输出示例展示了搜索结果的结构，包括文档ID、标题、内容、匹配分数和元数据。实际的输出将根据搜索查询和知识库中的文档而有所不同。
***
### FunctionDef update_docs_by_id(self, knowledge_base_name, docs)
**update_docs_by_id**: 此函数用于根据文档ID更新知识库中的文档。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要更新文档的知识库名称。
- `docs`: 字典类型，包含要更新的文档ID及其对应的更新内容。

**代码描述**:
`update_docs_by_id`函数主要通过发送HTTP POST请求到`/knowledge_base/update_docs_by_id`接口，实现对指定知识库中文档的更新操作。函数接收两个参数：`knowledge_base_name`和`docs`。`knowledge_base_name`参数指定了要更新文档所在的知识库名称，而`docs`参数则是一个字典，其中包含了文档ID及其对应的更新内容。

在函数内部，首先构造了一个包含`knowledge_base_name`和`docs`的字典`data`，然后调用`post`方法发送POST请求。`post`方法是`ApiRequest`类的一个成员方法，用于执行HTTP POST请求。在调用`post`方法时，将`/knowledge_base/update_docs_by_id`作为请求的URL，并将`data`字典作为JSON数据传递给该方法。

请求成功发送并接收到响应后，函数调用`_get_response_value`方法处理响应数据。`_get_response_value`是`ApiRequest`类的另一个成员方法，负责转换HTTP响应对象，并根据指定的参数返回处理后的数据。在本函数中，`_get_response_value`方法用于解析响应数据，并返回处理结果。

**注意**:
- 确保传入的`knowledge_base_name`和`docs`参数格式正确，且`docs`中的文档ID存在于指定的知识库中。
- 此函数的返回值依赖于`_get_response_value`方法的处理结果，通常为布尔值，表示更新操作是否成功。

**输出示例**:
假设更新操作成功，函数可能返回`True`。如果更新操作失败，可能返回`False`或者具体的错误信息。具体的返回值取决于`_get_response_value`方法的实现细节及服务器响应的内容。
***
### FunctionDef upload_kb_docs(self, files, knowledge_base_name, override, to_vector_store, chunk_size, chunk_overlap, zh_title_enhance, docs, not_refresh_vs_cache)
**upload_kb_docs**: 此函数用于上传文档到知识库，并可选择性地将文档内容添加到向量存储中。

**参数**:
- `files`: 文件列表，可以是字符串、路径对象或字节数据的列表。
- `knowledge_base_name`: 知识库名称，指定要上传文档的目标知识库。
- `override`: 布尔值，默认为False。如果为True，则在上传文件时覆盖同名文件。
- `to_vector_store`: 布尔值，默认为True。决定是否将上传的文档内容添加到向量存储中。
- `chunk_size`: 整数，指定文档分块的大小，默认值为CHUNK_SIZE。
- `chunk_overlap`: 整数，指定分块之间的重叠大小，默认值为OVERLAP_SIZE。
- `zh_title_enhance`: 布尔值，指定是否启用中文标题加强，默认值为ZH_TITLE_ENHANCE。
- `docs`: 字典，可用于提供文档的额外元数据，默认为空字典。
- `not_refresh_vs_cache`: 布尔值，默认为False。指定是否在添加文档到向量存储后刷新向量存储的缓存。

**代码描述**:
此函数首先将`files`参数中的每个文件转换为适合上传的格式。对于字节数据，将其包装为`BytesIO`对象；对于具有`read`方法的文件对象，直接使用；对于文件路径，将其打开为二进制读取模式。然后，构造一个包含所有必要信息的`data`字典，包括知识库名称、是否覆盖、是否添加到向量存储、分块大小、分块重叠、中文标题加强、文档元数据以及是否刷新向量存储的缓存。如果`docs`参数是字典，则将其转换为JSON字符串。最后，使用`post`方法向`/knowledge_base/upload_docs`路径发送POST请求，上传文件和相关数据，并通过`_get_response_value`方法处理响应，返回JSON格式的响应数据。

**注意**:
- 在上传大量数据或大文件时，考虑适当调整`chunk_size`和`chunk_overlap`参数以优化处理性能。
- 如果`to_vector_store`参数设置为True，确保知识库配置支持向量存储。
- 使用`docs`参数传递额外的文档元数据时，确保其格式正确，以便成功解析。

**输出示例**:
假设上传操作成功，函数可能返回如下格式的数据：
```python
{
    "code": 200,
    "msg": "上传成功",
    "data": {
        "failed_files": []
    }
}
```
如果上传过程中有文件因为各种原因失败，`failed_files`列表将包含这些文件的信息。
#### FunctionDef convert_file(file, filename)
**convert_file**: 此函数的功能是将不同类型的文件输入转换为文件名和文件对象的形式。

**参数**:
- **file**: 可以是字节串、具有read方法的文件对象或本地文件路径。
- **filename**: 可选参数，用于指定文件名。如果未提供，则会根据文件对象或路径自动确定文件名。

**代码描述**:
此函数处理三种类型的输入：
1. 如果输入是字节串（`bytes`），则将其转换为`BytesIO`对象，以便像文件一样操作。
2. 如果输入具有`read`方法（例如，已打开的文件对象），则直接使用该对象。如果提供了`filename`参数，则使用该参数值；如果未提供，则尝试从文件对象的`name`属性获取文件名。
3. 如果输入既不是字节串也没有`read`方法（即假定为本地文件路径），则尝试打开该路径指向的文件（以二进制读取模式），并自动确定文件名。如果提供了`filename`参数，则使用该参数值；如果未提供，则从路径中提取文件名。

**注意**:
- 输入的文件路径应该是有效且可访问的，否则在尝试打开文件时会引发异常。
- 当输入为字节串时，不会自动确定文件名，因此在这种情况下提供`filename`参数尤为重要。

**输出示例**:
假设有一个本地文件路径`"/path/to/document.pdf"`，调用`convert_file("/path/to/document.pdf")`将返回：
```
("document.pdf", <_io.BufferedReader name='/path/to/document.pdf'>)
```
这表示函数返回了文件名`"document.pdf"`和一个文件对象，后者可以用于进一步的文件操作。
***
***
### FunctionDef delete_kb_docs(self, knowledge_base_name, file_names, delete_content, not_refresh_vs_cache)
**delete_kb_docs**: 此函数用于从知识库中删除指定的文档。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要操作的知识库名称。
- `file_names`: 字符串列表，指定要删除的文件名称列表。
- `delete_content`: 布尔类型，默认为False，指定是否同时删除文件内容。
- `not_refresh_vs_cache`: 布尔类型，默认为False，指定是否不刷新向量搜索的缓存。

**代码描述**:
此函数首先构造一个包含知识库名称、文件名称列表、是否删除内容以及是否刷新向量搜索缓存的字典`data`。然后，调用`post`方法向`/knowledge_base/delete_docs`路径发送POST请求，请求体为`data`字典。最后，调用`_get_response_value`方法处理响应，并以JSON格式返回处理结果。

**注意**:
- 在调用此函数时，需要确保`knowledge_base_name`和`file_names`参数正确指向存在的知识库和文件，否则可能导致删除失败。
- `delete_content`参数控制是否删除文件的实际内容，如果设置为True，则文件将被完全删除；如果为False，则只从知识库的索引中移除文件，文件本身保留。
- `not_refresh_vs_cache`参数用于控制是否刷新向量搜索的缓存，如果为True，则在删除文件后不刷新缓存，这可能会影响后续的搜索结果准确性。

**输出示例**:
假设成功删除了指定的文件，函数可能返回如下的JSON对象：
```python
{
    "code": 200,
    "msg": "成功",
    "data": {
        "failed_files": []
    }
}
```
如果指定的文件不存在或删除失败，返回的JSON对象中`failed_files`列表将包含这些文件的名称。
***
### FunctionDef update_kb_info(self, knowledge_base_name, kb_info)
**update_kb_info**: 此函数用于更新知识库的信息。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要更新的知识库名称。
- `kb_info`: 字符串类型，提供知识库的新信息。

**代码描述**:
`update_kb_info`函数主要负责向后端发送请求，更新指定知识库的信息。它首先构造一个包含知识库名称(`knowledge_base_name`)和新的知识库信息(`kb_info`)的字典`data`。然后，使用`post`方法发送一个HTTP POST请求到`/knowledge_base/update_info`端点，携带上述`data`作为JSON数据。请求成功后，通过调用`_get_response_value`方法处理响应，如果指定`as_json=True`，则尝试将响应体解析为JSON格式并返回。

**注意**:
- 调用此函数时需要确保提供的知识库名称(`knowledge_base_name`)在系统中已存在，否则可能无法成功更新。
- 更新的信息(`kb_info`)应为字符串格式，可以包含知识库的描述、元数据等信息。
- 函数内部通过`post`方法发送HTTP请求，并通过`_get_response_value`方法处理响应，这两个方法的具体实现和异常处理机制对于理解函数行为非常重要。

**输出示例**:
假设更新知识库信息成功，返回的JSON响应可能如下：
```python
{
    "code": 200,
    "msg": "知识库信息更新成功",
    "data": {
        "knowledge_base_name": "example_kb",
        "kb_info": "更新后的知识库描述"
    }
}
```
此输出示例展示了一个典型的成功响应，其中包含状态码`200`、成功消息以及更新后的知识库名称和描述。实际返回的数据结构可能根据后端实现的不同而有所变化。
***
### FunctionDef update_kb_docs(self, knowledge_base_name, file_names, override_custom_docs, chunk_size, chunk_overlap, zh_title_enhance, docs, not_refresh_vs_cache)
**update_kb_docs**: 此函数用于更新知识库中的文档。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要更新文档的知识库名称。
- `file_names`: 字符串列表，包含需要更新的文件名。
- `override_custom_docs`: 布尔类型，默认为False，指定是否覆盖自定义文档。
- `chunk_size`: 整型，指定文档分块的大小，默认值由`CHUNK_SIZE`常量决定。
- `chunk_overlap`: 整型，指定文档分块之间的重叠大小，默认值由`OVERLAP_SIZE`常量决定。
- `zh_title_enhance`: 布尔类型，指定是否增强中文标题，默认值由`ZH_TITLE_ENHANCE`常量决定。
- `docs`: 字典类型，包含要更新的文档内容，默认为空字典。
- `not_refresh_vs_cache`: 布尔类型，默认为False，指定是否不刷新向量搜索缓存。

**代码描述**:
此函数首先构造一个包含所有参数的字典`data`，用于作为HTTP请求的负载。如果`docs`参数是字典类型，则将其转换为JSON字符串。然后，调用`post`方法向`/knowledge_base/update_docs`路径发送POST请求，请求体为`data`字典。最后，调用`_get_response_value`方法处理响应，如果指定`as_json`为True，则返回JSON格式的响应数据。

**注意**:
- 在调用此函数之前，确保知识库名称和文件名正确无误，以避免更新错误的文档。
- 当`override_custom_docs`为True时，将覆盖知识库中的自定义文档，需谨慎使用此选项。
- `chunk_size`和`chunk_overlap`参数影响文档分块的方式，不当的值可能影响搜索效果。
- 如果`docs`参数非空，函数将更新指定的文档内容；否则，仅更新文件名列表中的文件。
- `not_refresh_vs_cache`为True时，更新文档后不刷新向量搜索缓存，可能影响搜索结果的实时性。

**输出示例**:
```python
{
    "code": 200,
    "msg": "文档更新成功",
    "data": {
        "failed_files": []
    }
}
```
此示例表示更新操作成功执行，且所有指定的文件都已成功更新，没有失败的文件。
***
### FunctionDef recreate_vector_store(self, knowledge_base_name, allow_empty_kb, vs_type, embed_model, chunk_size, chunk_overlap, zh_title_enhance)
**recreate_vector_store**: 此函数用于重建知识库中的向量存储。

**参数**:
- `knowledge_base_name`: 字符串类型，指定要重建向量存储的知识库名称。
- `allow_empty_kb`: 布尔类型，默认为True，指定是否允许空的知识库。
- `vs_type`: 字符串类型，默认为`DEFAULT_VS_TYPE`，指定向量存储的类型。
- `embed_model`: 字符串类型，默认为`EMBEDDING_MODEL`，指定用于嵌入的模型。
- `chunk_size`: 整型，默认为`CHUNK_SIZE`，指定文本块的大小。
- `chunk_overlap`: 整型，默认为`OVERLAP_SIZE`，指定文本块之间的重叠大小。
- `zh_title_enhance`: 布尔类型，默认为`ZH_TITLE_ENHANCE`，指定是否增强中文标题。

**代码描述**:
函数首先构造一个包含所有参数的字典`data`，然后通过调用`self.post`方法，向`/knowledge_base/recreate_vector_store`路径发送POST请求，请求体为`data`字典。此请求旨在后端服务中重建指定知识库的向量存储。请求的响应通过`self._httpx_stream2generator`方法转换为生成器，以便以流的方式处理响应数据。如果`as_json`参数为True，则响应数据将被解析为JSON格式。

**注意**:
- 该函数依赖于`self.post`方法来发送HTTP POST请求，`self.post`方法的详细行为请参考其文档。
- `self._httpx_stream2generator`方法用于处理流式响应，其详细行为请参考其文档。
- 函数的执行结果依赖于后端服务的实现和状态，以及提供的参数是否符合后端服务的要求。

**输出示例**:
```python
[
    {"code": 200, "msg": "向量存储重建成功"},
    {"finished": 1, "total": 10, "msg": "正在处理..."},
    ...
]
```
此输出示例展示了函数返回值的可能形式，其中包含了多个字典，每个字典代表了重建过程中的一个状态或结果。`code`为200表示操作成功，`finished`和`total`字段表示当前处理进度，`msg`提供了额外的状态信息或错误消息。
***
### FunctionDef list_running_models(self, controller_address)
**list_running_models**: 此函数用于获取Fastchat中正运行的模型列表。

**参数**:
- `controller_address`: 字符串类型，可选参数，默认为None。用于指定控制器的地址。

**代码描述**: 
`list_running_models`函数主要通过发送HTTP POST请求到`/llm_model/list_running_models`端点，来获取当前Fastchat中正在运行的模型列表。函数首先构造一个包含`controller_address`的字典作为请求的数据。如果`log_verbose`变量为真，则会通过日志记录器记录发送的数据。随后，使用`post`方法发送请求，并通过`_get_response_value`方法处理响应，最终以JSON格式返回模型列表。如果响应中不存在"data"键，则默认返回空列表。

**注意**:
- 函数内部调用了`post`方法来执行HTTP POST请求，该方法的详细行为请参考`post`方法的文档。
- 函数还调用了`_get_response_value`方法来处理HTTP响应，该方法支持自定义处理逻辑，具体细节请参考`_get_response_value`方法的文档。
- 函数的执行依赖于`controller_address`参数，该参数用于指定控制器的地址，如果未提供，则默认为None。
- 函数的返回值是通过`_get_response_value`方法处理后的结果，通常是一个包含运行中模型信息的列表。

**输出示例**:
```python
[
    {
        "model_name": "model1",
        "status": "running",
        "controller_address": "192.168.1.100"
    },
    {
        "model_name": "model2",
        "status": "running",
        "controller_address": "192.168.1.101"
    }
]
```
此示例展示了函数可能的返回值，其中包含了两个正在运行的模型的信息，每个模型信息包括模型名称、状态以及控制器地址。
***
### FunctionDef get_default_llm_model(self, local_first)
**get_default_llm_model**: 此函数的功能是从服务器上获取当前运行的LLM（大型语言模型）模型名称及其运行位置（本地或在线）。

**参数**:
- `local_first`: 布尔值，默认为True。当设置为True时，函数会优先返回本地运行的模型；当设置为False时，会根据LLM_MODELS配置的顺序返回模型。

**代码描述**:
`get_default_llm_model`函数首先定义了两个内部函数`ret_sync`和`ret_async`，用于同步和异步环境下获取默认的LLM模型。函数根据`self._use_async`的值选择使用哪个内部函数。这两个内部函数的逻辑基本相同，区别在于`ret_async`使用了异步的方式来获取正在运行的模型列表。

函数逻辑如下：
1. 获取当前正在运行的模型列表。
2. 遍历配置中的LLM模型（LLM_MODELS），检查每个模型是否在运行列表中。
3. 如果找到了在运行列表中的模型，会根据`local_first`参数和模型是否为本地模型（通过检查`online_api`字段判断）来决定是否选择该模型。
4. 如果没有根据上述逻辑找到模型，那么会选择运行列表中的第一个模型作为默认模型。
5. 返回选择的模型名称和该模型是否为本地模型的信息。

在项目中，`get_default_llm_model`函数被用于不同的场景，例如在`test_get_default_llm`测试用例中验证函数返回值的类型，以及在`dialogue_page`函数中获取默认的LLM模型并在用户界面上显示当前运行的模型信息。这表明该函数在项目中扮演着获取当前有效LLM模型信息的关键角色，以便其他部分可以基于这些信息进行进一步的操作或显示。

**注意**:
- 在使用此函数时，需要确保`LLM_MODELS`配置正确，且`list_running_models`方法能够正确返回当前运行的模型列表。
- 函数的异步版本`ret_async`需要在支持异步的环境中运行。

**输出示例**:
```python
("gpt-3", True)
```
此输出表示当前运行的默认LLM模型为"gpt-3"，且该模型是本地运行的。
#### FunctionDef ret_sync
**ret_sync**: 此函数用于同步返回当前可用的本地或在线模型名称及其类型。

**参数**: 此函数不接受任何参数。

**代码描述**: `ret_sync`函数首先调用`list_running_models`方法获取当前正在运行的模型列表。如果没有模型正在运行，则返回一个空字符串和False。接下来，函数遍历预定义的模型列表`LLM_MODELS`，检查每个模型是否在运行中的模型列表里。如果找到一个在运行列表中的模型，会进一步检查该模型是否为本地模型（即不是通过在线API运行的模型）。如果`local_first`变量为真且当前模型不是本地模型，则继续检查下一个模型。如果找到符合条件的模型，则返回该模型名称和它是否为本地模型的布尔值。如果`LLM_MODELS`中的所有模型都不在运行中的模型列表里，则默认选择运行列表中的第一个模型，并返回其名称和它是否为本地模型的布尔值。

**注意**:
- `list_running_models`方法的返回值是关键，因为它决定了`ret_sync`函数能否找到有效的模型。该方法的详细行为请参考其文档。
- `local_first`变量控制优先选择本地模型还是在线模型，但在代码片段中未显示其定义，通常应在函数外部定义。
- 此函数假设`LLM_MODELS`是一个预定义的模型名称列表，用于指定优先考虑的模型顺序。
- 函数返回的模型名称和是否为本地模型的信息，可以用于后续操作，比如初始化模型或者决定使用哪个模型提供服务。

**输出示例**:
```python
("model1", True)
```
此示例表示函数返回了名为"model1"的模型，且该模型是本地运行的。
***
#### FunctionDef ret_async
**ret_async**: 此函数用于异步获取当前最适合的语言模型及其运行位置。

**参数**: 此函数不接受任何外部参数。

**代码描述**: `ret_async`函数首先通过调用`list_running_models`方法异步获取当前正在运行的模型列表。如果没有模型正在运行，则函数返回一个空字符串和False。接着，函数遍历预定义的语言模型列表`LLM_MODELS`，检查每个模型是否在运行中的模型列表里。对于每个正在运行的模型，函数检查该模型是否标记为本地运行（即不通过在线API运行）。如果`local_first`变量为真且模型不是本地运行的，则跳过该模型。一旦找到符合条件的模型，函数将其作为结果返回。如果`LLM_MODELS`中的所有模型都不在运行中的模型列表里，则选择`running_models`中的第一个模型作为结果返回。最后，函数根据模型是否通过在线API运行，返回模型名称和一个表示是否本地运行的布尔值。

此函数与`list_running_models`方法紧密相关，后者负责提供当前正在运行的模型列表。这种设计使得`ret_async`能够基于实时的模型运行状态，智能地选择最合适的模型进行操作。

**注意**: 
- 该函数是异步的，需要在支持异步操作的环境中运行。
- `local_first`变量控制是否优先选择本地运行的模型，但该变量的定义和赋值在代码片段之外，需要根据实际使用场景进行配置。
- 函数返回的模型名称为空字符串和布尔值False表示没有找到任何可用的模型。

**输出示例**:
```python
("model1", True)
```
此示例表示函数返回了名为"model1"的模型，且该模型是本地运行的。
***
***
### FunctionDef list_config_models(self, types)
**list_config_models**: 此函数用于获取服务器中配置的模型列表。

**参数**:
- `types`: 字符串列表，默认值为["local", "online"]。用于指定需要获取的模型类型。

**代码描述**:
`list_config_models`函数主要用于从服务器获取配置的模型列表。它接受一个参数`types`，这个参数是一个字符串列表，用于指定要获取的模型类型。默认情况下，这个列表包括"local"和"online"两种类型，分别代表本地模型和在线模型。

函数内部首先构造一个包含`types`的字典`data`，然后使用`self.post`方法向服务器发送一个POST请求，请求的URL为"/llm_model/list_config_models"，请求体为`data`字典。`self.post`方法是一个执行HTTP POST请求的函数，具体实现请参考`post`函数的文档。

请求成功返回后，函数使用`self._get_response_value`方法处理响应。`self._get_response_value`是一个转换HTTP响应对象的函数，它可以根据指定的参数返回处理后的数据。在本函数中，它被用来解析响应体，并尝试将其解析为JSON格式。如果解析成功，函数将返回一个字典，这个字典的结构为`{"type": {model_name: config}, ...}`，其中`type`是模型的类型，`model_name`是模型的名称，`config`是模型的配置信息。

**注意**:
- 函数依赖于`self.post`和`self._get_response_value`两个方法，确保这两个方法在使用前已正确实现。
- 返回的模型列表和配置信息的具体结构可能会根据服务器端的实现有所不同，请根据实际情况进行调整。

**输出示例**:
```python
{
    "local": {
        "model1": {"config1": "value1"},
        "model2": {"config2": "value2"}
    },
    "online": {
        "model3": {"config3": "value3"},
        "model4": {"config4": "value4"}
    }
}
```
此示例展示了函数可能的返回值，其中包含了两种类型的模型（"local"和"online"）及其配置信息。
***
### FunctionDef get_model_config(self, model_name)
**get_model_config**: 此函数用于获取服务器上指定模型的配置信息。

**参数**:
- `model_name`: 字符串类型，指定要查询配置的模型名称。默认值为None。

**代码描述**:
`get_model_config`函数首先构造一个包含模型名称的字典`data`，然后使用`post`方法向服务器发送请求，请求的URL为`"/llm_model/get_model_config"`。这里的`post`方法是`ApiRequest`类的一个成员方法，用于执行HTTP POST请求。请求成功返回的响应通过`_get_response_value`方法处理，以获取JSON格式的响应数据。`_get_response_value`是另一个`ApiRequest`类的成员方法，负责转换HTTP响应对象，并根据指定的参数返回处理后的数据。在本函数中，`_get_response_value`方法使用了一个lambda函数作为`value_func`参数，该lambda函数尝试从响应数据中获取`"data"`字段的值，如果不存在则返回空字典。

**注意**:
- 函数通过`post`方法发送HTTP POST请求，因此需要确保网络连接正常，且服务器能够正确处理该请求。
- 返回的模型配置信息以字典形式提供，具体包含的配置项取决于服务器端模型配置的实现细节。
- 如果服务器响应中不包含`"data"`字段，或者`model_name`参数指定的模型不存在，函数将返回空字典。

**输出示例**:
假设服务器上存在名为`"example_model"`的模型，其配置信息包括模型的版本号和支持的语言，那么函数的返回值可能如下所示：
```python
{
    "version": "1.0",
    "supported_languages": ["English", "Chinese"]
}
```
在实际使用中，返回的字典将包含服务器上指定模型的具体配置信息。
***
### FunctionDef list_search_engines(self)
**list_search_engines**: 此函数的功能是获取服务器支持的搜索引擎列表。

**参数**: 此函数没有参数。

**代码描述**: `list_search_engines` 函数首先通过调用 `post` 方法向服务器发送一个 HTTP POST 请求，请求的 URL 是 "/server/list_search_engines"。这个请求不需要任何额外的数据或参数。接收到服务器的响应后，函数利用 `_get_response_value` 方法处理这个响应。`_get_response_value` 方法被配置为以 JSON 格式解析响应内容，并通过一个 lambda 函数提取响应 JSON 中的 "data" 字段。如果 "data" 字段不存在，则默认返回一个空字典。最终，此函数返回一个包含搜索引擎名称的字符串列表。

**注意**:
- 函数依赖于 `post` 方法来发送 HTTP 请求，该方法提供了重试机制和异常处理，确保网络请求的稳定性。
- `_get_response_value` 方法用于解析 HTTP 响应，支持同步或异步模式，并允许通过自定义函数进一步处理解析后的数据。
- 返回的搜索引擎列表取决于服务器配置和可用性，可能会随时间或服务器设置的变化而变化。

**输出示例**:
```python
["Google", "Bing", "DuckDuckGo"]
```
此示例展示了函数可能返回的搜索引擎名称列表。实际返回的列表取决于服务器当前支持的搜索引擎。
***
### FunctionDef stop_llm_model(self, model_name, controller_address)
**stop_llm_model**: 此函数用于停止某个LLM模型。

**参数**:
- `model_name`: 字符串类型，指定要停止的LLM模型的名称。
- `controller_address`: 字符串类型，默认为None，指定控制器的地址。

**代码描述**:
`stop_llm_model`函数主要用于停止指定的LLM模型。在Fastchat的实现中，这通常意味着停止运行该LLM模型的`model_worker`。函数接收两个参数：`model_name`用于指定要停止的模型名称，`controller_address`用于指定控制器的地址，后者是可选的。

函数首先构造一个包含`model_name`和`controller_address`的字典`data`，然后通过调用`post`方法向`/llm_model/stop`路径发送POST请求，请求的数据体为`data`字典。`post`方法是`ApiRequest`类的一个成员方法，用于执行HTTP POST请求，并能够处理重试逻辑、异常捕获等。

在发送POST请求并接收到响应后，函数调用`_get_response_value`方法来处理响应。`_get_response_value`方法能够将HTTP响应对象转换为JSON格式（如果`as_json`参数为True），或者根据提供的`value_func`函数自定义处理逻辑。在本函数中，`as_json`参数被设置为True，意味着期望将响应体解析为JSON格式。

**注意**:
- 在使用此函数时，需要确保提供的`model_name`确实存在，并且有对应的`model_worker`在运行。
- 如果`controller_address`未指定，将使用默认的控制器地址。确保默认地址的正确性或显式提供地址参数。
- 函数的执行结果依赖于网络请求的成功与否，以及LLM模型的状态。因此，调用此函数后应检查返回的JSON数据，确认模型是否成功停止。

**输出示例**:
假设成功停止了名为`example_model`的LLM模型，函数可能返回如下JSON格式的数据：
```python
{
    "code": 200,
    "msg": "模型停止成功",
    "data": {
        "model_name": "example_model",
        "status": "stopped"
    }
}
```
此输出示例展示了一个成功的停止操作，其中`code`字段表示操作成功，`msg`字段提供了操作成功的消息，`data`字段包含了被停止模型的名称和其新状态。
***
### FunctionDef change_llm_model(self, model_name, new_model_name, controller_address)
**change_llm_model**: 此函数用于请求切换当前运行的大型语言模型(LLM)至另一个模型。

**参数**:
- `model_name`: 字符串类型，表示当前正在运行的模型名称。
- `new_model_name`: 字符串类型，表示要切换到的新模型名称。
- `controller_address`: 字符串类型，可选参数，默认为None，表示控制器的地址。

**代码描述**:
`change_llm_model` 函数首先检查`model_name`和`new_model_name`是否被指定，如果没有指定，则返回一个包含错误代码和消息的字典。接着，根据`self._use_async`的值决定是同步执行还是异步执行模型切换逻辑。

在同步(`ret_sync`)或异步(`ret_async`)执行逻辑中，首先获取当前正在运行的模型列表和配置中的模型列表。如果新模型名称与当前模型名称相同，或新模型已在运行中，则返回无需切换的消息。如果指定的当前模型未在运行中，或新模型未在配置中，则返回相应的错误消息。

如果检查通过，则构造一个包含模型名称和控制器地址的数据字典，通过POST请求向`/llm_model/change`端点发送请求，请求切换模型。最后，返回请求的响应值。

在项目中，`change_llm_model`函数被`webui_pages/dialogue/dialogue.py/dialogue_page`对象调用，用于处理用户通过界面选择切换LLM模型的操作。当用户选择一个新的模型并触发模型切换时，此函数负责向后端发送切换模型的请求，并处理响应，如显示成功或错误消息。

**注意**:
- 确保`model_name`和`new_model_name`正确指定，且新模型已在系统配置中定义。
- 异步执行需要在支持异步的环境中运行。

**输出示例**:
```json
{
    "code": 200,
    "msg": "模型切换成功"
}
```
或者在错误情况下:
```json
{
    "code": 500,
    "msg": "指定的模型'example_model'没有运行。当前运行模型：['model1', 'model2']"
}
```
#### FunctionDef ret_sync
**ret_sync**: 此函数用于同步切换模型，并返回切换结果。

**参数**: 此函数不接受任何外部参数。

**代码描述**: `ret_sync`函数首先调用`list_running_models`方法获取当前正在运行的模型列表。然后，它检查`new_model_name`是否等于`model_name`或是否已存在于运行模型列表中，如果是，则返回一个包含状态码200和消息"无需切换"的字典。如果指定的`model_name`不在运行模型列表中，则返回一个包含状态码500和相应错误消息的字典，指出指定模型未运行。接着，函数调用`list_config_models`方法获取配置中的模型列表，如果`new_model_name`不在配置模型列表中，则返回一个包含状态码500和错误消息的字典，指出要切换的模型未在配置中设置。

如果以上检查都通过，则构造一个包含`model_name`、`new_model_name`和`controller_address`的数据字典，使用`post`方法向`/llm_model/change`端点发送请求，请求切换模型。最后，调用`_get_response_value`方法处理响应，并以JSON格式返回结果。

**注意**:
- 函数内部逻辑依赖于`list_running_models`、`list_config_models`、`post`和`_get_response_value`四个方法，确保这些方法在使用前已正确实现。
- 函数中使用的`model_name`、`new_model_name`和`controller_address`变量应在函数外部定义并传递给函数，本文档中未显示这些变量的来源和定义方式。
- 返回的状态码和消息用于指示操作的结果，包括是否需要切换模型、指定模型是否运行以及是否在配置中找到要切换的模型。

**输出示例**:
```python
{
    "code": 200,
    "msg": "无需切换"
}
```
或
```python
{
    "code": 500,
    "msg": "指定的模型'model_name'没有运行。当前运行模型：['model1', 'model2']"
}
```
或
```python
{
    "code": 500,
    "msg": "要切换的模型'new_model_name'在configs中没有配置。"
}
```
此示例展示了函数可能的返回值，包括不需要切换、指定模型未运行和要切换的模型未配置等情况。
***
#### FunctionDef ret_async
**ret_async**: 此函数用于异步切换当前运行的语言模型。

**参数**: 此函数不接受任何外部参数。

**代码描述**: `ret_async` 函数首先通过调用 `list_running_models` 方法获取当前正在运行的模型列表。然后，它检查请求切换的新模型名称 `new_model_name` 是否已经是当前模型或已存在于运行模型列表中，如果是，则返回一个状态码为200的消息，表示无需切换。如果指定的当前模型 `model_name` 不在运行模型列表中，则返回一个状态码为500的消息，提示指定模型没有运行。接着，函数通过调用 `list_config_models` 方法获取配置中的模型列表，检查新模型名称是否在配置的模型列表中，如果不在，则返回一个状态码为500的消息，提示要切换的模型在配置中未找到。

如果以上检查都通过，函数将构造一个包含模型名称、新模型名称和控制器地址的数据字典，然后使用 `post` 方法向 `/llm_model/change` 端点发送请求以执行模型切换操作。最后，通过调用 `_get_response_value` 方法处理响应，并以JSON格式返回结果。

**注意**:
- 函数内部使用了 `self.list_running_models` 和 `self.list_config_models` 方法来获取当前运行的模型列表和配置的模型列表，确保这些方法能够正确返回所需的数据。
- 使用 `self.post` 方法发送HTTP请求，该方法的详细行为请参考 `post` 方法的文档。
- 使用 `_get_response_value` 方法来处理HTTP响应，该方法支持将响应体解析为JSON格式，具体细节请参考 `_get_response_value` 方法的文档。
- 函数的执行依赖于 `model_name`、`new_model_name` 和 `controller_address` 这几个变量的正确设置，这些变量需要在函数调用之前被正确赋值。

**输出示例**:
假设请求切换的新模型已经在运行或配置中不存在，函数可能返回以下示例之一的JSON格式数据：
```python
{
    "code": 200,
    "msg": "无需切换"
}
```
或
```python
{
    "code": 500,
    "msg": "指定的模型'model_name'没有运行。当前运行模型：['model1', 'model2']"
}
```
或
```python
{
    "code": 500,
    "msg": "要切换的模型'new_model_name'在configs中没有配置。"
}
```
***
***
### FunctionDef embed_texts(self, texts, embed_model, to_query)
**embed_texts**: 此函数用于对文本进行向量化，支持使用本地嵌入模型或在线支持嵌入的模型。

**参数**:
- `texts`: 字符串列表，表示需要进行向量化的文本列表。
- `embed_model`: 字符串类型，默认为`EMBEDDING_MODEL`，指定使用的嵌入模型。
- `to_query`: 布尔类型，默认为False，指示是否将结果用于查询。

**代码描述**:
`embed_texts`函数首先构造一个包含`texts`、`embed_model`和`to_query`的字典`data`，然后通过调用`post`方法向`/other/embed_texts`路径发送POST请求，请求体为`data`字典。此请求旨在获取指定文本的向量化表示。`post`方法负责执行HTTP POST请求，具体实现包括重试逻辑和异常处理，确保网络请求的健壮性。成功发送请求并接收响应后，`embed_texts`函数通过调用`_get_response_value`方法处理响应。`_get_response_value`方法负责转换HTTP响应，可以根据需要返回响应体的JSON解析结果或通过自定义函数进一步处理。在本函数中，`_get_response_value`使用了一个lambda函数作为`value_func`参数，该lambda函数接收响应的JSON解析结果，并返回其中的`data`字段，即向量化后的文本数据。

**注意**:
- 确保传入的`texts`参数为有效的文本列表，且`embed_model`参数指定的模型支持文本向量化。
- `to_query`参数应根据实际使用场景设置，以确保向量化结果的正确应用。
- 函数依赖于`post`和`_get_response_value`方法，确保这些方法能够正确处理HTTP请求和响应。

**输出示例**:
假设对两个文本`["你好", "世界"]`进行向量化，且函数成功执行，可能的返回值为：
```python
[
    [0.1, 0.2, 0.3, ...],  # "你好"的向量化表示
    [0.4, 0.5, 0.6, ...]   # "世界"的向量化表示
]
```
此输出示例展示了每个文本向量化后的浮点数列表，具体向量的维度和值取决于使用的嵌入模型。
***
### FunctionDef chat_feedback(self, message_id, score, reason)
**chat_feedback**: 此函数用于提交对话反馈评价。

**参数**:
- `message_id`: 字符串类型，指定需要反馈的消息ID。
- `score`: 整型，表示对话的评分。
- `reason`: 字符串类型，默认为空字符串，提供评分的原因。

**代码描述**:
`chat_feedback`函数主要用于收集用户对聊天消息的反馈，包括评分和原因。它通过构造一个包含`message_id`、`score`和`reason`的字典`data`，然后调用`post`方法向服务器的`/chat/feedback`路径发送POST请求，提交用户的反馈信息。`post`方法负责执行HTTP POST请求，并根据提供的参数发送数据。在成功发送请求并接收到响应后，`chat_feedback`函数通过调用`_get_response_value`方法处理响应数据，该方法负责转换HTTP响应对象，并根据指定的参数返回处理后的数据。最终，`chat_feedback`函数返回处理后的响应数据。

**注意**:
- 确保`message_id`和`score`参数正确无误，因为它们是提交反馈的关键信息。
- `score`参数应该是一个整数，代表用户对该消息的满意程度。
- `reason`参数虽然是可选的，但提供具体的反馈原因可以帮助改进服务或对话质量。
- 此函数的执行结果依赖于服务器的响应，因此需要确保服务器端正确处理反馈请求。

**输出示例**:
由于此函数的返回值依赖于服务器的响应，具体的输出示例将根据不同的请求URL和参数而有所不同。一般情况下，如果服务器处理成功，可能返回一个包含处理结果的整数值，例如`200`表示成功。
***
## ClassDef AsyncApiRequest
**AsyncApiRequest**: AsyncApiRequest 类的功能是提供异步 API 请求的封装。

**属性**:
- `base_url`: API 服务器的基础 URL。
- `timeout`: 请求超时时间，默认值由 `HTTPX_DEFAULT_TIMEOUT` 定义。
- `_use_async`: 表示是否使用异步模式，在此类中默认为 True。

**代码描述**:
AsyncApiRequest 类继承自 ApiRequest 类，专门用于处理异步 API 请求。它通过构造函数接收基础 URL 和超时时间作为参数，并在初始化时将 `_use_async` 属性设置为 True，这表明所有的请求都将以异步方式进行。这一设计使得 AsyncApiRequest 类能够在需要处理大量或长时间运行的网络请求时，提高程序的效率和响应性。

在项目中，AsyncApiRequest 类与 ApiRequest 类共同构成了 API 请求的核心处理机制。ApiRequest 类提供了基础的同步和异步请求处理能力，包括 GET、POST 和 DELETE 方法的封装，以及请求重试、流式请求和响应数据处理等功能。AsyncApiRequest 类通过继承 ApiRequest 类，专注于异步请求的处理，使得在需要异步处理网络请求的场景中，开发者可以更方便地实现高效的网络通信。

**注意**:
- 在使用 AsyncApiRequest 类时，需要确保传入的 `base_url` 参数正确指向目标 API 服务器。
- 由于 AsyncApiRequest 类处理的是异步请求，因此在调用其方法时，需要在相应的调用处使用 `await` 关键字，以确保异步操作能够正确执行并获取到结果。
- 在处理异步请求的过程中，可能会遇到网络延迟或服务器响应超时的情况，因此合理设置 `timeout` 参数对于提高程序的健壮性和用户体验非常重要。
### FunctionDef __init__(self, base_url, timeout)
**__init__**: 此函数的功能是初始化一个异步API请求对象。

**参数**:
- `base_url`: 字符串类型，代表API服务器的基础URL。默认值通过调用`api_address`函数获取。
- `timeout`: 浮点数类型，代表请求超时时间。默认值为`HTTPX_DEFAULT_TIMEOUT`。

**代码描述**: `__init__`函数是`AsyncApiRequest`类的构造函数，用于创建一个新的异步API请求对象。在这个函数中，首先通过调用父类的构造函数`super().__init__(base_url, timeout)`来初始化基础URL和超时时间。这里的`base_url`参数默认通过调用`api_address`函数获得，该函数从项目配置中读取并返回API服务器的地址。`timeout`参数则指定了网络请求的超时时间，默认值为`HTTPX_DEFAULT_TIMEOUT`，这是一个预设的常量，代表了HTTPX库中默认的请求超时时间。

接着，函数设置了一个私有属性`_use_async`为`True`，这表明该请求对象将使用异步方式进行网络请求。这是`AsyncApiRequest`类与同步请求类`ApiRequest`的主要区别之一，即它支持异步操作，能够在不阻塞主线程的情况下发送网络请求和接收响应。

**注意**: 使用`AsyncApiRequest`类时，需要确保`api_address`函数能够正确返回API服务器的地址，这要求项目的配置文件中已经正确设置了API服务器的`host`和`port`。此外，考虑到异步请求的特性，开发者在使用此类进行网络请求时应当熟悉Python的异步编程模式，如使用`async`和`await`关键字。
***
## FunctionDef check_error_msg(data, key)
**check_error_msg**: 该函数的功能是检查API请求返回的数据中是否包含错误信息，并返回相应的错误消息。

**参数**:
- `data`: 可以是字符串、字典或列表，表示API请求返回的数据。
- `key`: 字符串类型，默认值为"errorMsg"，表示在字典数据中查找错误信息的键名。

**代码描述**:
`check_error_msg`函数主要用于处理API请求后的响应数据，以判断是否发生了错误。它首先检查`data`参数的类型。如果`data`是一个字典，并且包含了指定的`key`（默认为"errorMsg"），则直接返回该键对应的值作为错误信息。如果字典中包含"code"键且其值不等于200，这通常表示请求未成功，函数将返回"msg"键对应的值作为错误信息。如果上述条件都不满足，函数将返回一个空字符串，表示没有发生错误。

在项目中，`check_error_msg`函数被多个地方调用，用于处理不同API请求的响应。例如，在`dialogue_page`和`knowledge_base_page`中，该函数用于检查与对话管理、知识库操作相关API请求的结果，以便在发生错误时向用户显示适当的错误消息。这有助于提高用户体验，通过即时反馈帮助用户了解操作失败的原因。

**注意**:
- 在使用`check_error_msg`函数时，需要确保传入的`data`参数格式正确，且与函数内部处理逻辑相匹配。
- 函数的返回值是一个字符串，可能是具体的错误信息或空字符串。调用方需要根据返回值判断是否需要进一步处理。

**输出示例**:
- 如果API返回的数据是`{"errorMsg": "无效的请求参数"}`，`check_error_msg`函数将返回"无效的请求参数"。
- 如果API返回的数据是`{"code": 404, "msg": "未找到资源"}`，函数将返回"未找到资源"。
- 如果API返回的数据不包含错误信息，函数将返回空字符串""。
## FunctionDef check_success_msg(data, key)
**check_success_msg**: 此函数的功能是检查API请求返回的数据中是否包含成功消息。

**参数**:
- `data`: 可以是字符串、字典或列表，代表API请求返回的数据。
- `key`: 字符串类型，默认值为"msg"，表示在返回的数据中查找成功消息的键。

**代码描述**:
`check_success_msg`函数主要用于处理API请求的返回数据，以确认是否成功执行了请求。函数首先检查`data`参数的类型是否为字典，并且该字典中是否包含`key`指定的键和"code"键。如果这些条件都满足，并且"code"的值为200，表示请求成功，函数将返回与`key`对应的值，通常是一个表示成功的消息。如果任一条件不满足，函数将返回一个空字符串，表示没有成功消息。

在项目中，`check_success_msg`函数被用于处理不同场景下API请求的返回值。例如，在`dialogue_page`和`knowledge_base_page`中，此函数用于检查更改LLM模型、上传知识库文档等操作的返回结果，以向用户反馈操作是否成功。通过检查返回数据中的"msg"键对应的值，可以向用户展示成功或错误的提示信息，从而提高用户体验。

**注意**:
- 确保API请求的返回数据格式符合函数处理的预期，特别是当预期返回数据为字典时，需要包含"code"和`key`指定的键。
- 函数返回的是一个字符串，可能是一个空字符串或包含成功消息的字符串。在使用此函数时，应根据返回值来决定后续的操作或显示逻辑。

**输出示例**:
- 如果API请求成功，并且返回的数据中包含`{"code": 200, "msg": "操作成功"}`，则`check_success_msg`函数将返回"操作成功"。
- 如果API请求失败，或返回的数据不包含"code"为200的情况，函数将返回一个空字符串。

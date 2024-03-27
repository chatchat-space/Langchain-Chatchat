## FunctionDef connect_sse(client, method, url)
**connect_sse**: 此函数的功能是连接到服务器发送事件（Server-Sent Events, SSE）流。

**参数**:
- `client`: 一个`httpx.Client`实例，用于执行HTTP请求。
- `method`: 字符串，指定HTTP请求的方法（如"GET"）。
- `url`: 字符串，指定请求的URL。
- `**kwargs`: 接收任意数量的关键字参数，这些参数将直接传递给`client.stream`方法。

**代码描述**:
`connect_sse`函数使用`httpx.Client`实例的`stream`方法建立一个到服务器的持久连接，用于接收服务器发送的事件流。这种机制通常用于实时数据传输场景，如实时消息推送、实时数据更新等。

函数首先通过`with`语句和`client.stream`方法建立一个上下文管理器，这确保了流的正确打开和关闭。`client.stream`方法被调用时，需要传入HTTP请求的方法（`method`）、请求的URL（`url`）以及任何其他关键字参数（`**kwargs`），这些参数可以包括请求头、查询参数等。

在成功建立连接并接收到响应后，函数使用`yield`关键字返回一个`EventSource`实例。`EventSource`是对服务器发送事件（SSE）流的封装，它允许调用者以一种简洁的方式处理接收到的事件。

**注意**:
- 使用此函数时，需要确保`httpx`库已正确安装并导入。
- 传递给此函数的URL应指向支持SSE的服务器端点。
- 在处理服务器发送的事件时，应注意异常处理和连接的稳定性，确保在网络不稳定或服务器端异常时能够正确处理或重连。
## FunctionDef generate_token(apikey, exp_seconds)
**generate_token**: 该函数用于生成带有过期时间的认证令牌。

**参数**:
- `apikey`: 字符串类型，用户的API密钥，通常由ID和密钥组成，中间以点分隔。
- `exp_seconds`: 整型，令牌的过期时间，单位为秒。

**代码描述**:
`generate_token` 函数首先尝试将传入的 `apikey` 按照点（`.`）分割成ID和密钥两部分。如果分割失败，会抛出异常，提示API密钥无效。之后，函数构造一个包含API密钥ID、过期时间戳（当前时间加上指定的过期秒数）、以及当前时间戳的负载（payload）。这个负载随后被用来生成JWT令牌，使用HS256算法进行编码，并附加一个包含算法和签名类型的头部信息。最终，函数返回这个编码后的令牌。

在项目中，`generate_token` 函数被 `ChatGLMWorker` 类的 `do_chat` 方法调用。在 `do_chat` 方法中，使用用户提供的API密钥和固定的过期时间（60秒）来生成令牌。这个令牌随后被用作HTTP请求的授权头部，以获取访问特定API接口的权限。这表明 `generate_token` 函数在项目中主要用于支持与外部服务的安全交互，确保请求在指定时间内有效。

**注意**:
- 确保传入的 `apikey` 格式正确，即包含ID和密钥，且以点分隔。
- 生成的令牌将基于传入的过期时间参数，确保合理设置以满足业务需求。
- 使用HS256算法要求密钥保持安全，避免泄露。

**输出示例**:
```python
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInNpZ25fdHlwZSI6IlNJR04ifQ.eyJhcGlfa2V5IjoiMTIzNDU2IiwiZXhwIjoxNjMwMjM0MDAwLCJ0aW1lc3RhbXAiOjE2MzAyMzM5NDAwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
```
此输出示例展示了一个编码后的JWT令牌，实际的令牌值将根据输入的 `apikey` 和 `exp_seconds` 以及当前时间而有所不同。
## ClassDef ChatGLMWorker
**ChatGLMWorker**: ChatGLMWorker类是用于处理基于GLM-4模型的聊天功能的工作器。

**属性**:
- `model_names`: 模型名称列表，默认为["zhipu-api"]。
- `controller_addr`: 控制器地址，用于与控制器进行通信。
- `worker_addr`: 工作器地址，用于接收来自控制器的请求。
- `version`: 模型版本，默认为"glm-4"。
- `context_len`: 上下文长度，默认为4096。

**代码描述**:
ChatGLMWorker类继承自ApiModelWorker类，专门用于处理基于GLM-4模型的聊天请求。在初始化过程中，该类接收模型名称、控制器地址、工作器地址等参数，并将这些参数传递给父类ApiModelWorker进行进一步的初始化。此外，ChatGLMWorker类还设置了默认的上下文长度为4096，并重写了父类的一些方法来实现具体的聊天功能。

`do_chat`方法是ChatGLMWorker类的核心功能，它接收一个ApiChatParams对象作为参数，该对象包含了聊天请求所需的所有信息。该方法首先加载配置，然后生成一个访问令牌，并构造请求头和请求体。之后，它向指定的URL发送POST请求，并处理响应结果。如果请求成功，它将从响应中提取文本内容，并以生成器的形式返回一个包含错误码和文本内容的字典。

`get_embeddings`方法用于打印嵌入信息，目前仅作为示例，没有实现具体功能。

`make_conv_template`方法用于创建一个会话模板，该方法接收一个会话模板字符串和模型路径作为参数，返回一个Conversation对象。该方法目前返回的Conversation对象包含了模型名称、系统消息、角色等信息，用于构建会话环境。

**注意**:
- 使用ChatGLMWorker类时，需要确保传入的参数正确，特别是`model_names`、`controller_addr`和`worker_addr`，这些参数对于确保工作器能够正确地与控制器通信至关重要。
- `do_chat`方法中的URL是硬编码的，如果API的地址发生变化，需要相应地更新这个地址。
- 由于`do_chat`方法使用了httpx.Client进行网络请求，需要确保环境中已安装httpx库。

**输出示例**:
```json
{
  "error_code": 0,
  "text": "这是由模型生成的回复文本。"
}
```
此输出示例展示了一个成功的聊天请求结果，其中`error_code`为0表示成功，`text`字段包含了模型生成的回复文本。
### FunctionDef __init__(self)
**__init__**: __init__函数的功能是初始化ChatGLMWorker对象。

**参数**:
- **model_names**: 一个字符串列表，默认值为["zhipu-api"]。这个列表包含了模型的名称。
- **controller_addr**: 一个字符串，表示控制器的地址。默认值为None。
- **worker_addr**: 一个字符串，表示工作器的地址。默认值为None。
- **version**: 一个字符串，指定模型的版本，默认值为"glm-4"。目前只支持"glm-4"版本。
- **kwargs**: 关键字参数，可以传递额外的参数给父类的初始化方法。

**代码描述**:
这个__init__方法是ChatGLMWorker类的构造函数，用于创建ChatGLMWorker对象的实例。在这个方法中，首先将`model_names`、`controller_addr`和`worker_addr`这三个参数通过关键字参数的形式更新到`kwargs`字典中。这样做是为了将这些参数传递给父类的初始化方法。接着，使用`setdefault`方法设置`kwargs`字典中`context_len`键的默认值为4096，如果`context_len`已经在`kwargs`中有值，则保持原值不变。之后，调用父类的__init__方法，并将更新后的`kwargs`字典传递给它。最后，将`version`参数的值赋值给实例变量`self.version`。

**注意**:
- 在使用ChatGLMWorker类创建对象时，需要注意`model_names`、`controller_addr`和`worker_addr`这三个参数都是可选的，但如果在特定环境下需要连接到特定的控制器或工作器，应当提供这些参数的值。
- `version`参数目前只支持"glm-4"版本，如果未来版本有更新，需要检查此处的默认值是否需要调整。
- 通过`kwargs`传递额外的参数时，应确保这些参数是父类初始化方法所支持的，以避免出现错误。
***
### FunctionDef do_chat(self, params)
**do_chat**: 该函数用于执行聊天操作，通过发送请求到指定的API接口，并返回聊天结果。

**参数**:
- `params`: ApiChatParams类型，用于定义聊天请求的参数。

**代码描述**:
`do_chat`函数首先调用`params.load_config`方法，加载与当前模型相关的配置信息。这一步骤确保了聊天操作能够根据模型的特定需求进行配置。随后，函数使用`generate_token`方法生成一个带有60秒过期时间的认证令牌，该令牌将用于API请求的授权。

函数接着构造了一个包含请求头的`headers`字典，其中`Content-Type`设置为`application/json`，并且`Authorization`字段包含了前面生成的令牌。此外，函数还构造了一个`data`字典，其中包含了聊天模型的版本、消息列表、最大令牌数、温度值以及一个指示是否流式传输的`stream`字段。

接下来，函数使用`httpx.Client`创建一个HTTP客户端，并通过POST方法向`https://open.bigmodel.cn/api/paas/v4/chat/completions`发送请求，请求体为`data`字典。请求成功后，函数解析响应内容，并通过生成器`yield`返回一个包含错误码和聊天内容的字典。

在整个过程中，`do_chat`函数与`generate_token`函数和`ApiChatParams`类的`load_config`方法紧密协作，确保了请求的安全性和配置的正确性，从而使得聊天操作能够顺利执行。

**注意**:
- 确保传入的`params`参数正确实例化，并且已经包含了所有必要的聊天请求信息。
- 生成的认证令牌具有时效性，因此在长时间的聊天会话中可能需要重新生成。
- 由于网络请求的不确定性，建议在使用此函数时添加异常处理逻辑，以确保程序的健壮性。
- 函数返回的是一个生成器，因此在使用返回值时需要通过迭代来获取实际的聊天结果。
***
### FunctionDef get_embeddings(self, params)
**get_embeddings**: 此函数的功能是打印嵌入信息和参数。

**参数**:
- `params`: 此参数用于接收传入的参数信息。

**代码描述**:
`get_embeddings` 函数是 `ChatGLMWorker` 类的一个方法，主要用于展示如何处理和打印传入的参数信息。在这个函数中，首先通过 `print("embedding")` 打印出字符串 "embedding"，表明当前操作是关于嵌入信息的处理。紧接着，通过 `print(params)` 打印出传入的参数 `params`，这有助于开发者了解当前处理的参数内容。

此函数虽然简单，但它为开发者提供了一个处理和展示参数信息的基本框架。在实际应用中，开发者可以在此基础上扩展更复杂的逻辑，比如对 `params` 进行解析和处理，然后生成相应的嵌入信息。

**注意**:
- 在使用此函数时，需要确保传入的 `params` 参数包含了所有必要的信息，以便函数能够正确地展示这些信息。
- 目前，此函数仅用于演示和打印参数信息，未涉及实际的嵌入信息生成逻辑。在将此函数应用于实际项目中时，可能需要对其进行相应的修改和扩展，以满足特定的业务需求。
***
### FunctionDef make_conv_template(self, conv_template, model_path)
**make_conv_template**: 该函数用于创建一个会话模板。

**参数**:
- **conv_template**: 字符串类型，指定会话模板的内容，可选参数，默认为None。
- **model_path**: 字符串类型，指定模型的路径，可选参数，默认为None。

**代码描述**:
`make_conv_template` 函数是用于生成一个会话模板的函数。它返回一个 `Conversation` 对象，该对象由几个关键部分组成：
- `name`：会话的名称，此处使用 `self.model_names[0]` 作为会话名称，假设 `self.model_names` 是一个列表，包含了模型的名称。
- `system_message`：系统消息，这里设置为 "你是智谱AI小助手，请根据用户的提示来完成任务"，这是在会话开始时系统自动发送的消息。
- `messages`：会话中的消息列表，这里初始化为空列表，表示会话开始时没有任何消息。
- `roles`：定义会话中的角色，这里定义了三个角色："user"（用户），"assistant"（助手）和"system"（系统）。
- `sep` 和 `stop_str`：分别定义了消息之间的分隔符和会话停止的字符串，这里使用 "\n###" 作为分隔符，"###" 作为停止字符串。

**注意**:
- 确保在调用此函数之前，`self.model_names` 已经被正确初始化，且至少包含一个元素。
- 该函数的参数 `conv_template` 和 `model_path` 在当前代码实现中未直接使用，但可以在扩展功能或自定义会话模板时提供额外的灵活性。

**输出示例**:
调用 `make_conv_template()` 函数可能返回如下的 `Conversation` 对象示例：
```
Conversation(
    name="模型名称",
    system_message="你是智谱AI小助手，请根据用户的提示来完成任务",
    messages=[],
    roles=["user", "assistant", "system"],
    sep="\n###",
    stop_str="###",
)
```
这个返回值展示了一个初始化状态的会话模板，其中包含了基本的会话设置但不包含任何实际的对话消息。
***

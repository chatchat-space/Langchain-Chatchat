## ClassDef TianGongWorker
**TianGongWorker**: TianGongWorker类是为了实现与天工API的交互而设计的，主要用于聊天和获取嵌入向量。

**属性**:
- `controller_addr`: 控制器地址，用于与模型控制器进行通信。
- `worker_addr`: 工作器地址，标识当前工作器的网络位置。
- `model_names`: 模型名称列表，默认为["tiangong-api"]。
- `version`: 模型版本，默认为"SkyChat-MegaVerse"。
- `context_len`: 上下文长度，默认为32768。

**代码描述**:
TianGongWorker类继承自ApiModelWorker类，提供了与天工API进行交互的方法。在初始化时，它接受控制器地址、工作器地址、模型名称列表和版本等参数，并将这些参数传递给父类构造函数。此外，它还设置了默认的上下文长度为32768。

该类重写了`do_chat`方法，用于实现与天工API的聊天功能。在这个方法中，它首先加载配置，然后构造请求数据和头部信息，包括通过MD5算法生成的签名。之后，它发起POST请求到天工API，并处理响应流。如果响应码为200，表示请求成功，它会从响应中提取文本并返回；如果响应码不为200，表示请求失败，它会记录错误信息并返回。

此外，TianGongWorker类还提供了`get_embeddings`和`make_conv_template`方法，但这些方法的具体实现在代码中未给出。

**注意**:
- 使用TianGongWorker类时，需要确保提供正确的API密钥和密钥签名，以通过天工API的身份验证。
- 在处理响应流时，需要注意正确处理流式数据，以避免数据丢失或解析错误。
- 该类的实现依赖于外部库requests和hashlib，因此在使用前需要确保这些库已正确安装。

**输出示例**:
调用`do_chat`方法可能的返回值示例：
```json
{
  "error_code": 0,
  "text": "这是天工API返回的回复文本。"
}
```
此示例展示了一个成功的API调用结果，其中`error_code`为0表示成功，`text`字段包含了天工API返回的回复文本。如果调用失败，`error_code`将不为0，并且`text`字段将包含错误信息。
### FunctionDef __init__(self)
**__init__**: __init__函数用于初始化TianGongWorker对象。

**参数**:
- `controller_addr`: 字符串类型，表示控制器的地址，默认值为None。
- `worker_addr`: 字符串类型，表示工作节点的地址，默认值为None。
- `model_names`: 字符串列表类型，表示模型名称，默认值为["tiangong-api"]。
- `version`: 字面量类型，表示版本，仅接受"SkyChat-MegaVerse"作为值，默认值为"SkyChat-MegaVerse"。
- `**kwargs`: 接收可变数量的关键字参数。

**代码描述**:
此函数是TianGongWorker类的构造函数，用于创建TianGongWorker实例。它接受几个参数，包括控制器地址(`controller_addr`)、工作节点地址(`worker_addr`)、模型名称列表(`model_names`)和版本(`version`)。此外，它还可以接受其他任意数量的关键字参数(`**kwargs`)。

函数首先将`model_names`、`controller_addr`和`worker_addr`参数更新到`kwargs`字典中。这意味着，如果这些参数被提供，它们将被用于更新或添加到`kwargs`中，这些`kwargs`随后将被用于父类的初始化。

接着，函数使用`setdefault`方法为`kwargs`设置一个默认的`context_len`值，如果`kwargs`中未提供`context_len`，则默认值为32768。

最后，通过`super().__init__(**kwargs)`调用父类的构造函数，传入更新后的`kwargs`，完成父类的初始化。同时，将`version`参数的值赋给实例变量`self.version`，以便后续使用。

**注意**:
- 在使用TianGongWorker类创建实例时，需要注意`controller_addr`和`worker_addr`参数是可选的，但在实际应用中，根据具体需求提供这些参数可能是必要的。
- `model_names`参数虽有默认值，但用户可以根据需要提供自定义模型名称列表。
- `version`参数目前仅支持"SkyChat-MegaVerse"这一版本，需要确保使用时的兼容性。
- 通过`**kwargs`参数，此函数提供了高度的灵活性，允许用户根据需要传入额外的配置选项。但使用时应注意确保传入的关键字参数与父类构造函数及TianGongWorker类的其他方法兼容。
***
### FunctionDef do_chat(self, params)
**do_chat**: 此函数的功能是通过调用外部API实现聊天功能，并处理返回的聊天数据。

**参数**:
- `params`: `ApiChatParams`类型，包含了进行聊天所需的参数，如消息列表、API密钥等。

**代码描述**:
`do_chat`函数首先调用`load_config`方法，为当前工作器加载配置。这一步骤确保了聊天请求能够根据特定的模型名称进行配置，从而使得聊天功能能够根据不同的模型需求灵活调整。

接着，函数定义了请求的URL和请求体数据。请求体中包含了消息列表和指定的模型名称"SkyChat-MegaVerse"。此外，为了确保请求的安全性，函数通过计算API密钥、密钥和当前时间戳的MD5哈希值来生成签名。

函数设置了请求头，其中包括了API密钥、时间戳、签名以及其他必要的信息，如内容类型和是否处理流式返回内容的标志。

通过`requests.post`方法发起对外部API的请求，函数使用了流式请求(`stream=True`)来实时处理返回的数据。在处理响应流时，函数逐行读取响应内容，并将每行数据解析为JSON格式。如果响应代码为200，表示请求成功，函数将累加聊天回复内容，并以生成器的形式逐步返回每次聊天的结果。如果响应代码不为200，函数将记录错误信息并以生成器的形式返回错误代码和错误消息。

**注意**:
- 在使用`do_chat`函数之前，确保已经正确配置了`ApiChatParams`中的参数，包括API密钥、密钥和消息列表等。
- 由于函数使用了生成器来逐步返回聊天结果，调用此函数时需要适当地处理生成器的迭代，以获取所有聊天回复。
- 函数中的错误处理机制确保了在遇到请求错误时能够及时记录并反馈错误信息，开发者应当注意检查错误日志，以便及时发现并解决问题。
- 本函数依赖于外部API进行聊天功能的实现，因此网络状况和API服务的稳定性可能会影响到聊天功能的表现和稳定性。
***
### FunctionDef get_embeddings(self, params)
**get_embeddings**: 此函数的功能是打印嵌入信息和参数。

**参数**:
- `params`: 此参数用于接收传入的参数信息，其具体内容和格式依调用时的实际情况而定。

**代码描述**:
`get_embeddings` 函数是 `TianGongWorker` 类的一个方法，主要用于展示如何处理和打印嵌入信息以及传入的参数。函数体内首先打印出字符串 "embedding"，随后打印出传入的 `params` 参数。这表明该函数的主要作用是在控制台上输出相关信息，以便于开发者进行调试或了解参数的传递情况。

**注意**:
- 由于此函数主要用于展示和调试目的，因此在实际生产环境中可能需要根据具体需求进行相应的修改或扩展。
- 参数 `params` 的内容和格式应根据实际使用场景事先定义好，以确保函数能够正确处理传入的数据。
- 当前函数实现较为简单，仅用于示例，因此在开发复杂应用时可能需要增加额外的逻辑来处理更复杂的数据结构或执行更复杂的操作。
***
### FunctionDef make_conv_template(self, conv_template, model_path)
**make_conv_template**: 该函数用于创建一个对话模板。

**参数**:
- **conv_template**: 字符串类型，指定对话模板，此版本中未使用。
- **model_path**: 字符串类型，指定模型路径，此版本中未使用。

**代码描述**:
`make_conv_template` 函数是 `TianGongWorker` 类的一个方法，它的主要作用是创建一个对话模板。该方法接受两个参数：`conv_template` 和 `model_path`，但在当前版本的实现中，这两个参数并没有被使用。函数返回一个 `Conversation` 对象，该对象是通过调用 `conv.Conversation` 构造函数创建的。创建的 `Conversation` 对象具有以下特点：
- `name` 属性被设置为 `self.model_names[0]`，即模型名称列表中的第一个名称。
- `system_message` 属性被设置为空字符串。
- `messages` 属性被设置为一个空列表，表示初始时对话中没有任何消息。
- `roles` 属性被设置为包含 "user" 和 "system" 的列表，表示对话中的角色。
- `sep` 属性被设置为 "\n### "，定义了消息之间的分隔符。
- `stop_str` 属性被设置为 "###"，定义了对话的结束标志。

**注意**:
- 尽管 `conv_template` 和 `model_path` 参数在当前版本中未被使用，但它们的存在预示着未来版本可能会支持根据模板或模型路径来定制对话模板。
- 创建的 `Conversation` 对象可以用于进一步的对话处理或模拟，但需要注意的是，初始状态下 `messages` 为空，表示尚未有任何对话内容。

**输出示例**:
假设 `self.model_names[0]` 的值为 "ExampleModel"，则函数的返回值可能如下所示：
```
Conversation(
    name="ExampleModel",
    system_message="",
    messages=[],
    roles=["user", "system"],
    sep="\n### ",
    stop_str="###",
)
```
这表示创建了一个名为 "ExampleModel" 的空对话模板，其中没有系统消息、没有任何对话内容，定义了用户和系统作为对话参与者的角色，以及消息分隔符和对话结束标志。
***

## ClassDef Ws_Param
**Ws_Param**: Ws_Param 类的功能是生成用于连接 Spark 服务的 URL。

**属性**:
- `APPID`: 应用程序的ID。
- `APIKey`: 用于访问Spark服务的API密钥。
- `APISecret`: 用于访问Spark服务的API密钥的秘密。
- `host`: 从Spark服务URL解析出的网络地址。
- `path`: 从Spark服务URL解析出的路径。
- `Spark_url`: Spark服务的完整URL。

**代码描述**:
Ws_Param 类通过初始化时传入的参数（APPID、APIKey、APISecret、Spark_url）来设置对象的基本属性。其中，`Spark_url`被解析为`host`和`path`，以便后续生成鉴权所需的签名。`create_url`方法用于生成最终的带有鉴权信息的URL。这个过程包括生成RFC1123格式的时间戳、拼接签名原文、使用HMAC-SHA256算法进行签名、将签名编码为Base64格式、构造Authorization头，并将这些鉴权参数编码后附加到原始URL上，生成最终的请求URL。

在项目中，`Ws_Param`类被`xinghuo.py`中的`request`函数调用，用于建立与Spark服务的WebSocket连接。`request`函数首先创建`Ws_Param`对象，通过调用其`create_url`方法获取鉴权后的URL，然后使用这个URL建立WebSocket连接，并发送请求数据。

**注意**:
- 确保传入`__init__`方法的`Spark_url`格式正确，因为它会被解析为`host`和`path`。
- 生成的URL包含敏感信息（如APIKey和APISecret），因此在日志或调试信息中打印URL时需要谨慎。

**输出示例**:
生成的URL可能看起来像这样：
```
https://spark.example.com/api?authorization=Base64EncodedString&date=RFC1123Date&host=spark.example.com
```
这个URL包含了所有必要的鉴权信息，可以直接用于建立与Spark服务的连接。
### FunctionDef __init__(self, APPID, APIKey, APISecret, Spark_url)
**__init__**: 该函数用于初始化Ws_Param类的实例。

**参数**:
- `APPID`: 应用程序的ID。
- `APIKey`: 用于访问Spark API的API密钥。
- `APISecret`: 用于访问Spark API的API密钥的秘密。
- `Spark_url`: Spark服务的URL地址。

**代码描述**:
此函数是`Ws_Param`类的构造函数，负责初始化类的实例。它接收四个参数：`APPID`、`APIKey`、`APISecret`以及`Spark_url`。这些参数分别用于存储应用程序ID、API密钥、API密钥的秘密以及Spark服务的URL地址。

函数内部，首先将传入的`APPID`、`APIKey`、`APISecret`和`Spark_url`参数分别赋值给实例变量`self.APPID`、`self.APIKey`、`self.APISecret`和`self.Spark_url`。这样做是为了在类的其他方法中可以方便地使用这些值。

接着，函数使用`urlparse`函数（来自Python标准库中的`urllib.parse`模块）解析`Spark_url`参数。`urlparse`函数会返回一个解析结果对象，该对象包含了URL的不同组成部分。本函数中，特别使用了该对象的`netloc`和`path`属性来获取URL的网络位置（即主机名加端口号）和路径，分别赋值给实例变量`self.host`和`self.path`。这样的设计使得在需要与Spark服务进行通信时，可以方便地构造请求。

**注意**:
- 在使用`Ws_Param`类之前，确保提供的`Spark_url`是有效的，并且可以解析为正确的网络位置和路径。
- `APPID`、`APIKey`和`APISecret`需要从Spark服务的管理界面获取，确保这些信息的准确性和安全性。
- 本函数不对传入的参数值进行有效性验证，调用者需要确保提供的参数值是合法且适用于目标Spark服务的。
***
### FunctionDef create_url(self)
**create_url**: 此函数的功能是生成用于WebSockets连接的URL，包含鉴权信息。

**参数**: 此函数不接受任何外部参数，但使用了对象内部的多个属性，包括`self.host`、`self.path`、`self.APISecret`、`self.APIKey`以及`self.Spark_url`。

**代码描述**: `create_url`函数首先生成一个符合RFC1123标准的时间戳，然后构造一个用于签名的原始字符串，该字符串包含了请求的主机、日期和请求行信息。接下来，使用HMAC-SHA256算法对这个字符串进行加密，加密所用的密钥是API密钥的秘密部分。加密完成后，将加密结果转换为Base64格式的字符串，这个字符串将作为鉴权头的一部分。最后，函数将鉴权信息、日期和主机信息组合成一个字典，然后将这个字典转换为URL编码格式，并附加到`self.Spark_url`之后，形成最终的URL。

在项目中，`create_url`函数被`xinghuo.py`中的`request`函数调用。在`request`函数中，首先创建`Ws_Param`对象，然后调用`create_url`生成WebSocket连接所需的URL。这个URL包含了所有必要的鉴权信息，确保了连接的安全性。之后，`request`函数使用这个URL建立WebSocket连接，并通过这个连接发送和接收数据。

**注意**: 使用此函数时，需要确保`Ws_Param`对象已经被正确初始化，包括API密钥、API秘密、主机地址等信息。此外，生成的URL中包含的鉴权信息是基于当前时间的，因此生成的URL应立即使用，避免因时间差导致鉴权失败。

**输出示例**: 假设`self.Spark_url`为`"https://api.example.com/connect"`，`self.host`为`"api.example.com"`，生成的URL可能如下所示：
```
"https://api.example.com/connect?authorization=dGhpcyBpcyBhIGZha2UgYXV0aG9yaXphdGlvbiBzdHJpbmc%3D&date=Mon%2C%2020%20Sep%202023%2012%3A00%3A00%20GMT&host=api.example.com"
```
此URL包含了编码后的鉴权信息、日期和主机地址，可用于建立安全的WebSocket连接。
***
## FunctionDef gen_params(appid, domain, question, temperature, max_token)
**gen_params**: 该函数用于根据appid和用户的提问来生成请求参数。

**参数**:
- **appid**: 应用程序的唯一标识符。
- **domain**: 请求的领域或类别。
- **question**: 用户的提问内容。
- **temperature**: 生成回答时的创造性控制参数。
- **max_token**: 生成回答的最大令牌数。

**代码描述**:
`gen_params` 函数负责构建一个用于发送到Spark API的请求数据结构。这个数据结构包括三个主要部分：`header`、`parameter`和`payload`。在`header`部分，包含了`app_id`和一个固定的`uid`。`parameter`部分定义了与生成回答相关的一些参数，如领域(`domain`)、随机阈值(`random_threshold`)、最大令牌数(`max_tokens`)、审核级别(`auditing`)和创造性控制参数(`temperature`)。`payload`部分则包含了用户的提问(`question`)。这个结构使得Spark API能够理解请求的上下文和需求，从而生成相应的回答。

在项目中，`gen_params` 函数被`xinghuo.py`中的`request`函数调用。在`request`函数中，首先通过`SparkApi.Ws_Param`创建了一个WebSocket URL，然后调用`gen_params`函数生成请求参数，最后通过WebSocket连接发送这些参数，并处理返回的数据。这表明`gen_params`函数是与Spark API进行交互的关键一环，它负责生成符合API要求的请求数据。

**注意**:
- 确保传入的`appid`、`domain`、`question`、`temperature`和`max_token`参数值正确，因为这些直接影响到请求的成功与否以及返回的结果。
- `temperature`参数控制生成文本的创造性，较高的值会导致更多样化的回答，而较低的值则使回答更加确定性。
- `max_token`参数限制了生成回答的长度，需要根据实际需求调整。

**输出示例**:
```json
{
  "header": {
    "app_id": "your_appid",
    "uid": "1234"
  },
  "parameter": {
    "chat": {
      "domain": "your_domain",
      "random_threshold": 0.5,
      "max_tokens": 100,
      "auditing": "default",
      "temperature": 0.7
    }
  },
  "payload": {
    "message": {
      "text": "你的问题"
    }
  }
}
```
此输出示例展示了一个典型的请求数据结构，其中包含了应用ID、领域、问题文本以及控制生成回答行为的参数。

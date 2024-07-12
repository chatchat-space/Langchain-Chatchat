# Agent 和 Function Call

如果您希望寻找本框架的 Agent 部分，您可以参考 `libs/chatchat-server/chatchat/server/agent`,这里包含了目前框架中所有的Agent内容。

## Agent Factory

Agent Factory 中用于存储特殊的 Agent 模型，目前，拥有两个系列，分别是：

+ GLM 系列：包含 GLM-3，GLM-4 开源模型。
+ Qwen系列：支持Qwen-2，Qwen1.5 开源模型。

## Tool Factory

Tool Factory 中用于存储特殊的工具，目前，Chatchat已经自带了多个工具，分别是：

+ 高德地图POI搜索工具：利用高德地图API进行POI搜索，根据指定位置和类型返回相关地点的信息。
+ 高德地图天气查询工具：利用高德地图API获取指定城市的天气信息。
+ 音频问答工具：处理音频问题，使用提供的音频文件和文本问题来生成答案。
+ ARXIV论文工具：使用Arxiv.org进行搜索并检索各个领域的科学文章。
+ 数学计算器工具：用于进行简单数学计算，将用户的问题转换为可以由numexpr评估的数学表达式。
+ 互联网搜索工具：使用指定的搜索引擎在互联网上搜索并获取信息。
+ 本地知识库工具：使用本地知识库进行搜索，根据指定的数据库和查询获取信息。
+ 油管视频工具：使用该工具搜索YouTube视频。
+ 系统命令工具：使用Shell执行系统命令。
+ 文生图工具：根据用户的描述生成图片。
+ Prometheus对话工具：将自然语言转换为PromQL并在Prometheus服务器中执行查询，返回执行结果。
+ 数据库对话工具：将自然语言转换为SQL并在数据库中执行查询，返回执行结果。
+ 图片对话工具：根据图片和文本问题生成回答，并在图片上绘制矩形框。
+ 天气查询工具：查询指定城市的当前天气情况。
+ 维基百科搜索工具：使用维基百科进行搜索。
+ WolframAlpha工具：计算复杂的公式和执行高级数学运算。

## 增加自己的工具

我们支持使用 LangChain方式来增加自己的工具，您可以参考 `libs/chatchat-server/chatchat/server/agent/tools_registry`
中的工具模板，来增加自己的工具。
一个简单的构建方式是：

1. 新建一个 py 文件，用于书写自己的工具实现，例如

```python
@regist_tool(title="数学计算器")
def calculate(text: str = Field(description="a math expression")) -> float:
    """
    Useful to answer questions about simple calculations.
    translate user question to a math expression that can be evaluated by numexpr.
    """
    import numexpr

    try:
        ret = str(numexpr.evaluate(text))
    except Exception as e:
        ret = f"wrong: {e}"

    return BaseToolOutput(ret)
```

+ 使用 `@regist_tool` 装饰器用于注册工具。
+ 填写需要传入的参数以及传入参数对应的函数。
+ 使用 `BaseToolOutput` 来封装工具的顺畅。

2. 如果你想使用 LangChain 自带的工具，可以这么使用，这里列举了一个使用 LangChain Shell 工具的例子。

```python
from langchain_community.tools import ShellTool
from chatchat.server.pydantic_v1 import Field
from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="系统命令")
def shell(query: str = Field(description="The command to execute")):
    """Use Shell to execute system shell commands"""
    tool = ShellTool()
    return BaseToolOutput(tool.run(tool_input=query))
```

这个例子在LangChain工具的基础上实例化工具，并作为Chatchat可以使用的工具进行调用。

## 让模型知道要调用工具

除了添加工具，在用户传入提示词的时候，也尽可能的强调需要使用工具，这样能提升模型调用工具的概率。比如

#### search_internet

使用这个工具是因为用户需要在联网进行搜索。这些问题通常是你不知道的，这些问题具有特点，
例如：

+ 联网帮我查询 xxx
+ 我想知道最新的新闻
  或者，用户有明显的意图，需要获取事实的信息。
  返回字段如下

```
search_internet
```

#### search_local_knowledge

使用这个工具是希望用户能够获取本地的知识，这些知识通常是你自身能力不具备的专业问题，或者用户指定了某个任务的。
例如：

+ 告诉我 关于 xxx 的 xxx 信息
+ xxx 中 xxx 的 xxx 是什么
  返回字段如下

```
search_local_knowledge
```

## 优化Agent系统提示词

如果您的模型不兼容 / 不适配 LangChain 默认的 Struct Agent提示词模板。您可以在 配置文件中的 `prompt_settings.yaml`自定义提示词。
例如：GLM-3 模型的提示词为：

```
You can answer using the tools.Respond to the human as helpfully and
accurately as possible.\nYou have access to the following tools:\n{tools}\nUse
a json blob to specify a tool by providing an action key (tool name)\nand an action_input
key (tool input).\nValid \"action\" values: \"Final Answer\" or  [{tool_names}]\n
Provide only ONE action per $JSON_BLOB, as shown:\n\n```\n{{{{\n  \"action\":
$TOOL_NAME,\n  \"action_input\": $INPUT\n}}}}\n```\n\nFollow this format:\n\n
Question: input question to answer\nThought: consider previous and subsequent
steps\nAction:\n```\n$JSON_BLOB\n```\nObservation: action result\n... (repeat
Thought/Action/Observation N times)\nThought: I know what to respond\nAction:\n\
```\n{{{{\n  \"action\": \"Final Answer\",\n  \"action_input\": \"Final response
to human\"\n}}}}\nBegin! Reminder to ALWAYS respond with a valid json blob of
a single action. Use tools if necessary.\nRespond directly if appropriate. Format
is Action:```$JSON_BLOB```then Observation:.\nQuestion: {input}\n\n{agent_scratchpad}\n
```

同时，如果您的模型返回格式不适配 LangChain 默认的 Struct Agent，您需要像 GLM-3 / GLM-4 一样自定义Agent执行逻辑，以确保能正确返回
Function Call的内容。

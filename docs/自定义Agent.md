## 自定义属于自己的Agent
### 1. 创建自己的Agent工具
+ 开发者在```server/agent```文件中创建一个自己的文件，并将其添加到```tools.py```中。这样就完成了Tools的设定。

+ 当您创建了一个```custom_agent.py```文件，其中包含一个```work```函数，那么您需要在```tools.py```中添加如下代码：
```python
from custom_agent import work
Tool.from_function(
    func=work,
    name="该函数的名字",
    description=""
    )
```
+ 请注意，如果你确定在某一个工程中不会使用到某个工具，可以将其从Tools中移除，降低模型分类错误导致使用错误工具的风险。

### 2. 修改 custom_template.py文件
开发者需要根据自己选择的大模型设定适合该模型的Agent Prompt和自自定义返回格式。
在我们的代码中，提供了默认的两种方式，一种是适配于GPT和Qwen的提示词：
```python
"""
    Answer the following questions as best you can. You have access to the following tools:
    
    {tools}
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    history:
    {history}
    
    Question: {input}
    Thought: {agent_scratchpad}
"""
```

另一种是适配于GLM-130B的提示词：
```python
"""
尽可能地回答以下问题。你可以使用以下工具:{tools}
请按照以下格式进行:
Question: 需要你回答的输入问题
Thought: 你应该总是思考该做什么
Action: 需要使用的工具，应该是[{tool_names}]中的一个
Action Input: 传入工具的内容
Observation: 行动的结果
       ... (这个Thought/Action/Action Input/Observation可以重复N次)
Thought: 我现在知道最后的答案
Final Answer: 对原始输入问题的最终答案

现在开始！

之前的对话:
{history}

New question: {input}
Thought: {agent_scratchpad}
"""
```

### 3. 局限性
1. 在我们的实验中，小于70B级别的模型，若不经过微调，很难达到较好的效果。因此，我们建议开发者使用大于70B级别的模型进行微调，以达到更好的效果。
2. 由于Agent的脆弱性，temperture参数的设置对于模型的效果有很大的影响。我们建议开发者在使用自定义Agent时，对于不同的模型，将其设置成0.1以下，以达到更好的效果。
3. 即使使用了大于70B级别的模型，开发者也应该在Prompt上进行深度优化，以让模型能成功的选择工具并完成任务。


### 4. 我们已经支持的Agent
我们为开发者编写了三个运用大模型执行的Agent，分别是：
1. 翻译工具，实现对输入的任意语言翻译。
2. 数学工具，使用LLMMathChain 实现数学计算。
3. 天气工具，使用自定义的LLMWetherChain实现天气查询，调用和风天气API。
4. 我们支持Langchain支持的Agent工具，在代码中，我们已经提供了Shell和Google Search两个工具的实现。
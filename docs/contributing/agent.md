# Agent 和 Function Call

如果您希望寻找本框架的 Agent 部分，您可以参考 `libs/chatchat-server/chatchat/server/agent`,这里包含了目前框架中所有的Agent内容。

## Agent Factory

Agent Factory 中用于存储特殊的 Agent 模型，目前，拥有两个系列，分别是：

+ GLM 系列：包含 GLM-3，GLM-4模型。
+ Qwen系列：支持Qwen-2，Qwen1.5 模型。

## Tool Factory

Tool Factory 中用于存储特殊的工具，目前，Chatchat已经自带了多个工具，分别是：

+ 

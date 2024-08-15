from typing import Dict,Any
from .nodes_registry import regist_nodes

#node1
@regist_nodes(title="节点1",description="这是节点1的描述")
def node1(*args: Any,**kwargs)-> Dict[str, any]:

    #通过关键字参数获取输入参数
    question=kwargs["question"]
    print(f"node1_function: {question}")
    return {"question":question, "node1_output_1":"这是节点1输出参数node1_output_1的值，会被存入全局state['state']中","node1_output_2":"这是节点1输出参数node1_output_2的值，会被存入全局state['state']中"}
from typing import Dict,Any
from .nodes_registry import regist_nodes
#node4
@regist_nodes(title="节点4",description="这是节点4的描述")
def node4(*args: Any,**kwargs)-> Dict[str, any]:

    #通过关键字参数获取输入参数
    node4_input_1=kwargs["node4_input_1"]
    node4_input_2=kwargs["node4_input_2"]
    #打印参数
    print(f"node4_function: {node4_input_1},{node4_input_2}")
    return {"node4_output_1":"这是节点4输出参数node4_output_1的值，会被存入全局state['state']中","node4_output_2":"这是节点4输出参数node4_output_2的值，会被存入全局state['state']中"}
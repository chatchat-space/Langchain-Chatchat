from typing import Dict,Any
from .nodes_registry import regist_nodes
#node3
@regist_nodes(title="节点3",description="这是节点3的描述")
def node3(*args: Any,**kwargs)-> Dict[str, any]:

    #通过关键字参数获取输入参数
    node3_input_1=kwargs["node3_input_1"]
    node3_input_2=kwargs["node3_input_2"]
    #打印参数
    print(f"node3_function: {node3_input_1},{node3_input_2}")
    return {"node3_output_1":"这是节点3输出参数node3_output_1的值，会被存入全局state['state']中","node3_output_2":"这是节点3输出参数node3_output_2的值，会被存入全局state['state']中"}
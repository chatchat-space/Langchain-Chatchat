
# import sys
# import os
# # 获取当前文件的完整路径  
# current_file_path = os.path.abspath(__file__)  
# # 当前文件所在目录  
# current_dir = os.path.dirname(current_file_path)  
# # 向上遍历四级目录  
# for _ in range(4):  
#     current_dir = os.path.dirname(current_dir) 
# sys.path.append(current_dir)
import importlib
from typing import Any, Callable, Dict, List

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.graph import (
    CompiledGraph,
)
from typing_extensions import TypedDict

from chatchat.server.langgraph import node_factory

importlib.reload(node_factory)
from chatchat.server.langgraph.node_factory.nodes_registry import _NODES_REGISTRY

memory = MemorySaver()

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        data: all state dict
    """
    #因为TypedDict很难动态构建，因此定义一个Dict类型state字段，用于保存所有langgraph的state
    state: Dict

def is_conditional_true(state,reference_node:str,output_name:str,operator:str,value_type,value)->bool:

    if value_type == "constant":
        value=value
    elif value_type == "reference":
        reference_node_output_name_to_compare= value
        reference_node_to_compare=reference_node_output_name_to_compare.split(".")[0]
        output_name_to_compare=reference_node_output_name_to_compare.split(".")[1]
        value=state["state"][reference_node_to_compare][output_name_to_compare]

    if reference_node not in state["state"]: 
        return False
    
    if operator == "==":
        if state["state"][reference_node][output_name] == value:
            return True
    elif operator == "!=":
        if state["state"][reference_node][output_name] != value:
            return True
    elif operator == "in":
        if value in state["state"][reference_node][output_name]:
            return True
        
    return False

#通用的全局state状态条件判断，用于判断全局state的某个字段是否满足某个条件,满足则返回设定的下一个节点的名称，可满足大部分使用场景
#复杂的添加判断，用户需自行添加代码实现
def wrapper_common_conditional(conditional_edge:Dict)->Callable:
    def common_conditional(state) -> str:
        if_else_conditions = conditional_edge["if_else_conditions"]
        for if_condition in if_else_conditions:
            logic=if_condition["logic"]
            conditions=if_condition["contditions"]
            next_path = if_condition["next_path"]
            if conditions is None or len(conditions) == 0:
                continue
            #如果逻辑是and，所有条件都满足则返回下一个节点
            if logic == "and":
                is_all_true=True
                for condition in conditions:
                    reference_node_output_name = condition["reference_node_output_name"]
                    reference_node=reference_node_output_name.split(".")[0]
                    output_name=reference_node_output_name.split(".")[1]
                    operator = condition["operator"]
                    value_type = condition["value_type"]
                    value = condition["value"]
                    if is_conditional_true(state,reference_node,output_name,operator,value_type,value)==False:
                        is_all_true=False
                        break
                
                if is_all_true:
                    return next_path
            #如果逻辑是or，有一个条件满足则返回下一个节点
            elif logic == "or":
                for condition in conditions:
                    reference_node_output_name = condition["reference_node_output_name"]
                    reference_node=reference_node_output_name.split(".")[0]
                    output_name=reference_node_output_name.split(".")[1]
                    operator = condition["operator"]
                    value_type = condition["value_type"]
                    value = condition["value"]
                    if is_conditional_true(state,reference_node,output_name,operator,value_type,value):
                        return next_path
                    
        return conditional_edge["default_path"]
    return common_conditional

def wrapper_state_function(node:Dict)->Callable:
    def do_node_function(state):
        node_id=node["id"]
        node_name=node["data"]["name"]
        node_function=_NODES_REGISTRY[node_name]
        input_kwargs={}
        for arg in node["data"]["input_args"]:
            if arg["value_type"]=="reference":
                reference_node_output_name= arg["value"]
                reference_node=reference_node_output_name.split(".")[0]
                output_name=reference_node_output_name.split(".")[1]
                input_kwargs[arg["param_name"]]=state["state"][reference_node][output_name]
            if arg["value_type"]=="constant":
                input_kwargs[arg["param_name"]]=arg["value"]

        return_value:Dict=node_function(**input_kwargs)

        output_kwargs={}
        for out_arg in node["data"]["output_args"]:
            output_kwargs[out_arg]=return_value[out_arg]

        node_output_kwargs={node_id:output_kwargs}
        #更新state["state"]状态，保留所有字段
        state["state"].update(node_output_kwargs)
        print(state)
        return state
    return do_node_function

def wrapper_human_feedback_state_function(node:Dict)->Callable:
    def human_feedback(state):
        print("---human_feedback---")
        return state
    return human_feedback

def should_continue(state):
    return "end"
def build_flow(flow_params:Dict)->CompiledGraph:
    handle_flow(flow_params)
    workflow = StateGraph(GraphState)
    
    interrupt_before=[]
    #添加节点
    for node in flow_params["nodes"]:
        print("添加节点：",node["id"])
        if node["type"] == "start_node" or node["type"] == "end":
            continue
        if node["type"] =="user_input_node":
            workflow.add_node(node["id"], wrapper_human_feedback_state_function(node))
            interrupt_before.append(node["id"])
            continue

        workflow.add_node(node["id"], wrapper_state_function(node))
    #添加边
    for edge in flow_params["edges"]:
        print("添加边：",edge)
        workflow.add_edge(edge["source"], edge["target"])
    #添加条件边
    #如果存在key，conditional_edges
    if "conditional_edges" in flow_params:
        for conditional_edge in flow_params["conditional_edges"]:
            print("添加条件边：",conditional_edge)
            workflow.add_conditional_edges(conditional_edge["source"], wrapper_common_conditional(conditional_edge))
    
    # Compile
    app = workflow.compile(checkpointer=memory,interrupt_before=interrupt_before)


    # try:
    #     app.get_graph().draw_mermaid_png(output_file_path="flow.png")
    #     # display(Image(app.get_graph().draw_mermaid_png()))
    # except Exception:
    #     # This requires some extra dependencies and is optional
    #     pass
    return app



flow={
        'id': '27ade7f6-8110-4b78-b8ce-5e9b586b158d',
        'flowName': '测试流程',
        'flowDescription': '测试',
        'nodes': [
            {
                'id': '__start__',
                'position': {'x': -1612.4018400379443, 'y': 45.8579359249552},
                'type': 'start_node',
                'data': {
                    'name': '开始节点',
                    'description': '这是开始节点',
                    'input_args': [{'param_name': 'question', 'value': '', 'type': 'userinput'}],
                    'output_args': ['question']
                },
                'measured': {'width': 535, 'height': 300},
                'selected': False,
                'dragging': False
            },
            {
                'id': '__end__',
                'position': {'x': 667.6864856771989, 'y': 30.499268174754775},
                'type': 'end',
                'data': {'name': 'END', 'description': '这是结束节点', 'input_args': [], 'output_args': []},
                'measured': {'width': 140, 'height': 100},
                'selected': False,
                'dragging': False
            },
            {
                'id': 'LLM-1726983096034',
                'position': {'x': -1141.2291713167017, 'y': -163.3450066882027},
                'type': 'llm_node',
                'data': {
                    'flowId': '27ade7f6-8110-4b78-b8ce-5e9b586b158d',
                    'name': 'LLM',
                    'description': '大模型会话',
                    'input_args': [
                        {'param_name': 'model', 'value': 'qwen-max', 'value_type': 'constant', 'show_type': 'customer'},
                        {'param_name': 'temperature', 'value': '0.5', 'value_type': 'constant', 'show_type': 'customer'},
                        {
                            'param_name': 'prompt_template',
                            'value': '对下面的问题换一种问法：\n{question1}',
                            'value_type': 'constant',
                            'show_type': 'customer'
                        },
                        {'param_name': 'question1', 'value': '__start__.question', 'value_type': 'reference', 'show_type': 'general'}     
                    ],
                    'output_args': ['answer']
                },
                'measured': {'width': 488, 'height': 300},
                'selected': False,
                'dragging': False
            },
            {
                'id': '条件判断-1726984014966',
                'position': {'x': -726.4824484382189, 'y': -212.2810960234359},
                'type': 'condition_node',
                'data': {
                    'flowId': '27ade7f6-8110-4b78-b8ce-5e9b586b158d',
                    'name': '条件判断',
                    'description': '输出参数条件判断',
                    'if_else_conditions': [
                        {
                            'id': 'if-else-1726984014966',
                            'logic': 'and',
                            'contditions': [
                                {
                                    'reference_node_output_name': 'LLM-1726983096034.answer',
                                    'operator': 'in',
                                    'value_type': 'constant',
                                    'value': '200'
                                }
                            ],
                            'next_path': ''
                        },
                        {
                            'id': 'if-else-1726984450325',
                            'logic': 'and',
                            'contditions': [
                                {
                                    'reference_node_output_name': 'LLM-1726983096034.answer',
                                    'operator': 'in',
                                    'value_type': 'constant',
                                    'value': '100'
                                }
                            ],
                            'next_path': ''
                        }
                    ],
                    'default_path': '__end__'
                },
                'measured': {'width': 666, 'height': 300},
                'selected': False,
                'dragging': False
            },
            {
                'id': 'LLM-1726984199650',
                'position': {'x': 21.684456116397087, 'y': -480.03047637725217},
                'type': 'llm_node',
                'data': {
                    'flowId': '27ade7f6-8110-4b78-b8ce-5e9b586b158d',
                    'name': 'LLM',
                    'description': '大模型会话',
                    'input_args': [
                        {'param_name': 'model', 'value': 'qwen-max', 'value_type': 'constant', 'show_type': 'customer'},
                        {'param_name': 'temperature', 'value': 0.1, 'value_type': 'constant', 'show_type': 'customer'},
                        {
                            'param_name': 'prompt_template',
                            'value': '把下面的话中的数字变为中文大写：\n{question}',
                            'value_type': 'constant',
                            'show_type': 'customer'
                        },
                        {
                            'param_name': 'question',
                            'value': 'LLM-1726983096034.answer',
                            'value_type': 'reference',
                            'show_type': 'general'
                        }
                    ],
                    'output_args': ['answer']
                },
                'measured': {'width': 488, 'height': 300},
                'selected': False,
                'dragging': False
            },
            {
                'id': 'LLM-1726984423604',
                'position': {'x': 15.93521325239692, 'y': 126.05173015128025},
                'type': 'llm_node',
                'data': {
                    'flowId': '27ade7f6-8110-4b78-b8ce-5e9b586b158d',
                    'name': 'LLM',
                    'description': '大模型会话',
                    'input_args': [
                        {'param_name': 'model', 'value': 'qwen-max', 'value_type': 'constant', 'show_type': 'customer'},
                        {'param_name': 'temperature', 'value': 0.1, 'value_type': 'constant', 'show_type': 'customer'},
                        {
                            'param_name': 'prompt_template',
                            'value': '把下面的话中的数字变为英文：\n{question}',
                            'value_type': 'constant',
                            'show_type': 'customer'
                        },
                        {
                            'param_name': 'question',
                            'value': 'LLM-1726983096034.answer',
                            'value_type': 'reference',
                            'show_type': 'general'
                        }
                    ],
                    'output_args': ['answer']
                },
                'measured': {'width': 488, 'height': 300},
                'selected': False,
                'dragging': False
            }
        ],
        'edges': [
            {'source': '__start__', 'target': 'LLM-1726983096034', 'id': 'xy-edge____start__-LLM-1726983096034'},
            {
                'source': 'LLM-1726983096034',
                'target': '条件判断-1726984014966',
                'id': 'xy-edge__LLM-1726983096034-条件判断-1726984014966'
            },
            {
                'source': '条件判断-1726984014966',
                'sourceHandle': 'if-else-1726984014966',
                'target': 'LLM-1726984199650',
                'id': 'xy-edge__条件判断-1726984014966if-else-1726984014966-LLM-1726984199650'
            },
            {
                'source': '条件判断-1726984014966',
                'sourceHandle': 'if-else-1726984450325',
                'target': 'LLM-1726984423604',
                'id': 'xy-edge__条件判断-1726984014966if-else-1726984450325-LLM-1726984423604'
            },
            {'source': 'LLM-1726984423604', 'target': '__end__', 'id': 'xy-edge__LLM-1726984423604-__end__'},
            {'source': 'LLM-1726984199650', 'target': '__end__', 'id': 'xy-edge__LLM-1726984199650-__end__'}
        ]
    }


def handle_flow(flow_params:Dict):
    #处理flow_params数据，将flow格式的数据转为类似flow_params_example的数据，提取构造conditional_edges数组
    flow_params["conditional_edges"]=[]
    for node in flow_params["nodes"]:
        if node["type"] == "condition_node":
            #从nodes中删除该node
            flow_params["nodes"].remove(node)
            node_id=node["id"]
            #遍历edges，找出target为node_id的edge，找出source
            source=""
            for edge in flow_params["edges"]:
                if edge["target"] == node_id:
                    #从edges中删除该edge
                    flow_params["edges"].remove(edge)
                    source=edge["source"]
                    break
            if_else_conditions=[]
            for if_else_condition in node["data"]["if_else_conditions"]:
                condition_id=if_else_condition["id"]
                #遍历edges，找出sourceHandle为condition_id的edge，找出target作为next_path
                next_path=""
                for edge in flow_params["edges"]:
                    # edge如果存在sourceHandle字段
                    if "sourceHandle" not in edge:
                        continue
                    if edge["sourceHandle"] == condition_id:
                        #从edges中删除该edge
                        flow_params["edges"].remove(edge)
                        next_path=edge["target"]
                        break
                new_condition={
                    "logic":if_else_condition["logic"],
                    "contditions":if_else_condition["contditions"],
                    "next_path":next_path
                }
                if_else_conditions.append(new_condition)
            
            default_path="__end__"
            #遍历edges，找出source为node_id的，sourceHandle为ifelse-default的，找出target，作为default_path，然后从edges中删除该edge
            for edge in flow_params["edges"]:
                if edge["source"] == node_id and edge["sourceHandle"] == "ifelse-default":
                    #从edges中删除该edge
                    flow_params["edges"].remove(edge)
                    default_path=edge["target"]
                    break
            flow_params["conditional_edges"].append({
                "source":source,
                "if_else_conditions":if_else_conditions,
                "default_path":default_path
            })
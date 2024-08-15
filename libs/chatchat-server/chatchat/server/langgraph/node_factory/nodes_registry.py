from typing import Any, Callable, Dict, Optional, Tuple, Type, Union
_NODES_REGISTRY = {}

def regist_nodes(
    *args: Any,
    title: str = "",
    description: str = "",
) -> Callable:
    """
    wrapper of langgraph node decorator
    add node to regstiry automatically
    """
    def decorator(def_func: Callable):
        _NODES_REGISTRY[def_func.__name__] = def_func
        # def wrapper(*args, **kwargs):
        #     result = def_func(*args, **kwargs)
        #     return result
        return def_func
    return decorator
from typing import Callable, Any, Dict, Optional, Type, Union

__all__ = ["regist_graph"]

_GRAPHS_REGISTRY: Dict[str, Callable] = {}


def regist_graph(name: str) -> Callable:
    """
    装饰器，用于注册图到注册表中
    :param name: 图的名称
    :return: 被装饰的函数
    """
    def wrapper(func: Callable) -> Callable:
        _GRAPHS_REGISTRY[name] = func
        return func
    return wrapper

import logging
import os
from typing import Any, AnyStr, Callable, Dict, List, OrderedDict

import yaml


def get_position_map(
    folder_path: AnyStr,
    file_name: str = "_position.yaml",
) -> Dict[str, int]:
    """
    Get the mapping from name to index from a YAML file
    :param folder_path:
    :param file_name: the YAML file name, default to '_position.yaml'
    :return: a dict with name as key and index as value
    """
    try:
        position_file_name = os.path.join(folder_path, file_name)
        if not os.path.exists(position_file_name):
            return {}

        with open(position_file_name, encoding="utf-8") as f:
            positions = yaml.safe_load(f)
        position_map = {}
        for index, name in enumerate(positions):
            if name and isinstance(name, str):
                position_map[name.strip()] = index
        return position_map
    except:
        logging.warning(
            f"Failed to load the YAML position file {folder_path}/{file_name}."
        )
        return {}


def sort_by_position_map(
    position_map: Dict[str, int],
    data: List[Any],
    name_func: Callable[[Any], str],
) -> List[Any]:
    """
    Sort the objects by the position map.
    If the name of the object is not in the position map, it will be put at the end.
    :param position_map: the map holding positions in the form of {name: index}
    :param name_func: the function to get the name of the object
    :param data: the data to be sorted
    :return: the sorted objects
    """
    if not position_map or not data:
        return data

    return sorted(data, key=lambda x: position_map.get(name_func(x), float("inf")))


def sort_to_dict_by_position_map(
    position_map: Dict[str, int],
    data: List[Any],
    name_func: Callable[[Any], str],
) -> OrderedDict[str, Any]:
    """
    Sort the objects into a ordered dict by the position map.
    If the name of the object is not in the position map, it will be put at the end.
    :param position_map: the map holding positions in the form of {name: index}
    :param name_func: the function to get the name of the object
    :param data: the data to be sorted
    :return: an OrderedDict with the sorted pairs of name and object
    """
    sorted_items = sort_by_position_map(position_map, data, name_func)
    return OrderedDict([(name_func(item), item) for item in sorted_items])

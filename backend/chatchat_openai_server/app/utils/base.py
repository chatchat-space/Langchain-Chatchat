import json
import uuid


def gen_id(prefix='') -> str:
    return str(prefix + uuid.uuid4().hex)


def get_valid_var(*objs):
    for var in objs:
        if var:
            return var
    return None


def to_dict(_data) -> dict:
    if isinstance(_data, str):
        data = json.loads(_data)
    else:
        data = _data
    return data

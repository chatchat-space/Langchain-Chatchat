import uuid


def gen_id(prefix='') -> str:
    return str(prefix + uuid.uuid4().hex)


def get_valid_var(*objs):
    for var in objs:
        if var:
            return var
    return None

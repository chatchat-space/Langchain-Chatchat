import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from server.model_workers.azure import request_azure_api
from pprint import pprint


def test_azure():
    messages = [{"role": "user", "content": "hello"}]

    for x in request_azure_api(messages):
        print(type(x))
        pprint(x)
        assert x.choices is not None

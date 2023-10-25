import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from webui_pages.utils import ApiRequest

import pytest
from pprint import pprint
from typing import List


api = ApiRequest()


def test_get_default_llm():
    llm = api.get_default_llm_model()
    
    print(llm)
    assert isinstance(llm, tuple)
    assert isinstance(llm[0], str) and isinstance(llm[1], bool)


def test_server_configs():
    configs = api.get_server_configs()
    pprint(configs, depth=2)

    assert isinstance(configs, dict)
    assert len(configs) > 0


def test_list_search_engines():
    engines = api.list_search_engines()
    pprint(engines)

    assert isinstance(engines, list)
    assert len(engines) > 0


@pytest.mark.parametrize("type", ["llm_chat", "agent_chat"])
def test_get_prompt_template(type):
    print(f"prompt template for: {type}")
    template = api.get_prompt_template(type=type)

    print(template)
    assert isinstance(template, str)
    assert len(template) > 0

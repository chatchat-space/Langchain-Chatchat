import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

from pprint import pprint
from typing import List

import pytest

from chatchat.webui_pages.utils import ApiRequest

api = ApiRequest()


@pytest.mark.parametrize("type", ["llm_model"])
def test_get_prompt_template(type):
    print(f"prompt template for: {type}")
    template = api.get_prompt_template(type=type)

    print(template)
    assert isinstance(template, str)
    assert len(template) > 0

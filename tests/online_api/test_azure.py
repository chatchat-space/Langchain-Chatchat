import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
from server.model_workers.azure import request_azure_api
import pytest
from configs import TEMPERATURE, ONLINE_LLM_MODEL
@pytest.mark.parametrize("version", ["azure-api"])
def test_azure(version):
    messages = [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "介绍一下自己"}]
    for resp in request_azure_api(
            messages=messages,
            api_base_url=ONLINE_LLM_MODEL["azure-api"]["api_base_url"],
            api_key=ONLINE_LLM_MODEL["azure-api"]["api_key"],
            deployment_name=ONLINE_LLM_MODEL["azure-api"]["deployment_name"],
            api_version=ONLINE_LLM_MODEL["azure-api"]["api_version"],
            temperature=TEMPERATURE,
            max_tokens=1024,
            model_name="azure-api"
    ):
        assert resp["code"] == 200


if __name__ == "__main__":
    test_azure("azure-api")
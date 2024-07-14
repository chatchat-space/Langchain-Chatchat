from open_chatcaht.api_client import ApiClient

API_URI_GET_SERVER_CONFIGS = "/server/configs"
API_URI_GET_PROMPT_TEMPLATE = "/server/prompt_template"


class ServerClient(ApiClient):
    # 服务器信息
    def get_server_configs(self, **kwargs) -> dict:
        response = self._post(API_URI_GET_SERVER_CONFIGS, **kwargs)
        return self._get_response_value(response, as_json=True)

    def get_prompt_template(
            self,
            type: str = "llm_chat",
            name: str = "default",
            **kwargs,
    ) -> str:
        data = {
            "type": type,
            "name": name,
        }
        response = self._post(API_URI_GET_PROMPT_TEMPLATE, json=data, **kwargs)
        return self._get_response_value(response, value_func=lambda r: r.text)

#coding=utf8

import os
from langchain.utilities import BingSearchAPIWrapper


env_bing_key = os.environ.get("BING_SUBSCRIPTION_KEY")
env_bing_url = os.environ.get("BING_SEARCH_URL")


def search(text, result_len=3):
    if not (env_bing_key and env_bing_url):
        return [{"snippet":"please set BING_SUBSCRIPTION_KEY and BING_SEARCH_URL in os ENV",
            "title": "env inof not fould", "link":"https://python.langchain.com/en/latest/modules/agents/tools/examples/bing_search.html"}]
    search = BingSearchAPIWrapper()
    return search.results(text, result_len)


if __name__ == "__main__":
    r = search('python')

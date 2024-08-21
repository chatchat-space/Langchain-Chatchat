# -*- coding: utf-8 -*-
import logging
import logging.config
import os
import re
from openai import OpenAI

from langchain_chatchat.utils.try_parse_json_object import try_parse_json_object

logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = os.getenv("ZHIPUAI_API_KEY")

GLM_JSON_RESPONSE_PREFIX = """You should always follow the instructions and output a valid JSON object.
The structure of the JSON object you can found in the instructions, use {"answer": "$your_answer"} as the default structure
if you are not sure about the structure.

And you should always end the block with a "```" to indicate the end of the JSON object.

<instructions>
"""

GLM_JSON_RESPONSE_SUFFIX = """Output:
</instructions>

"""
# TODO </instructions>下方需要有一个换行符 \r\n

PATTERN = re.compile(r"```(?:json\s+)?(\W.*?)```", re.DOTALL)
"""Regex pattern to parse the output."""


def test_json_output(logging_conf):
    logging.config.dictConfig(logging_conf)  # type: ignore
    client = OpenAI(
        # api_key="YOUR_API_KEY",
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )
    system_prompt = """帮我抽取文本中的事实信息和重要内容. Please parse the "question" and "answer" and output them in JSON format. 
  

"""
    user_prompt = """First, MAP works for binary relevance. MAP is designed to evaluate a ranking or recommender system with a binary relevance function. NDCG can handle both binary and graded relevance. This is useful when you deal with use cases like search: the documents are usually not wholly relevant or irrelevant but exist on a particular scale. 

Second, NDCG and MAP account for diminishing ranks differently. Both NDCG and MAP at K consider the order of items and thus are suitable when you care about ranking quality. However, they treat decreasing ranks differently. 

MAP gives more weight to the relevant items at the top of the list. Since the metric is based on Precision values at each relevant position in the ranked list, it is more sensitive to changes in the early positions. Any non-relevant items at the beginning of the list influence the aggregation at each subsequent Precision calculation and contribute to the overall MAP score. MAP drops more rapidly if there are non-relevant items at the top.

DCG assigns diminishing weights to items as you move down the list, but they are logarithmic. The contribution of items decreases, but not extremely rapidly. Check out this video for a walkthrough explanation: DCG has a sharper elbow and a heavier tail compared to the more rapid descent of MAP as you move down the K.
  """

    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[{"role": "system", "content": f"{GLM_JSON_RESPONSE_PREFIX}{system_prompt}"},
                    {"role": "user", "content": f"{user_prompt}{GLM_JSON_RESPONSE_SUFFIX}"}],
        top_p=0.7,
        temperature=0.1,
        max_tokens=2000,
    )
    logger.info("\033[1;32m" + f"client: {response}" + "\033[0m")

    action_match = PATTERN.search(response.choices[0].message.content)
    if action_match is not None:
        json_text, json_object = try_parse_json_object(action_match.group(1).strip())

        logger.info("\033[1;32m" + f"json_text: {json_text}" + "\033[0m")
        logger.info("\033[1;32m" + f"json_object: {json_object}" + "\033[0m")

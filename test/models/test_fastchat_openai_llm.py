import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
import asyncio
from argparse import Namespace
from models.loader.args import parser
from models.loader import LoaderCheckPoint


import models.shared as shared



async def dispatch(args: Namespace):
    args_dict = vars(args)

    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)

    llm_model_ins = shared.loaderLLM()
    llm_model_ins.set_api_base_url("http://localhost:8000/v1")
    llm_model_ins.call_model_name("chatglm-6b")
    history = [
        ("which city is this?", "tokyo"),
        ("why?", "she's japanese"),

    ]
    for answer_result in llm_model_ins.generatorAnswer(prompt="她在做什么? ", history=history,
                                                       streaming=False):
        resp = answer_result.llm_output["answer"]

        print(resp)

if __name__ == '__main__':
    args = None
    args = parser.parse_args(args=['--model-dir', '/media/checkpoint/',  '--model', 'fastChatOpenAI', '--no-remote-model'])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dispatch(args))

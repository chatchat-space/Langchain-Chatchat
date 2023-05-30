import sys
import os
import argparse
import asyncio
from argparse import Namespace
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
from chains.dialogue_answering import *
from langchain.llms import OpenAI
from models.base import (BaseAnswer,
                         AnswerResult)
import models.shared as shared
from models.loader.args import parser
from models.loader import LoaderCheckPoint

async def dispatch(args: Namespace):

    args_dict = vars(args)
    shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    llm_model_ins = shared.loaderLLM()
    if not os.path.isfile(args.dialogue_path):
        raise FileNotFoundError(f'Invalid dialogue file path for demo mode: "{args.dialogue_path}"')
    llm = OpenAI(temperature=0)
    dialogue_instance = DialogueWithSharedMemoryChains(zero_shot_react_llm=llm, ask_llm=llm_model_ins, params=args_dict)

    dialogue_instance.agent_chain.run(input="What did David say before, summarize it")


if __name__ == '__main__':

    parser.add_argument('--dialogue-path', default='', type=str, help='dialogue-path')
    parser.add_argument('--embedding-model', default='', type=str, help='embedding-model')
    args = parser.parse_args(['--dialogue-path', '/home/dmeck/Downloads/log.txt',
                              '--embedding-mode', '/media/checkpoint/text2vec-large-chinese/'])
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dispatch(args))

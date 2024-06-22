"""Usage
调用默认模型：
python server/api_allinone.py

加载多个非默认模型：
python server/api_allinone.py --model-path-address model1@host1@port1 model2@host2@port2 

多卡启动：
python server/api_allinone.py --model-path-address model@host@port --num-gpus 2 --gpus 0,1 --max-gpu-memory 10GiB

"""
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import uvicorn
from api import create_app
from llm_api_stale import controller_args, launch_all, parser, server_args, worker_args

parser.add_argument("--api-host", type=str, default="0.0.0.0")
parser.add_argument("--api-port", type=int, default=7861)
parser.add_argument("--ssl_keyfile", type=str)
parser.add_argument("--ssl_certfile", type=str)

api_args = ["api-host", "api-port", "ssl_keyfile", "ssl_certfile"]


def run_api(host, port, **kwargs):
    app = create_app()
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(
            app,
            host=host,
            port=port,
            ssl_keyfile=kwargs.get("ssl_keyfile"),
            ssl_certfile=kwargs.get("ssl_certfile"),
        )
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    print("Luanching api_allinone，it would take a while, please be patient...")
    print("正在启动api_allinone，LLM服务启动约3-10分钟，请耐心等待...")
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)
    launch_all(
        args=args,
        controller_args=controller_args,
        worker_args=worker_args,
        server_args=server_args,
    )
    run_api(
        host=args.api_host,
        port=args.api_port,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
    )
    print("Luanching api_allinone done.")
    print("api_allinone启动完毕.")

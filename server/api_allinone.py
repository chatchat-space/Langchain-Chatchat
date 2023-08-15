"""Usage
调用默认模型：
python server/api_allinone.py

加载多个非默认模型：
python server/api_allinone.py --model-path-address model1@host1@port1 model2@host2@port2 

多卡启动：
python server/api_allinone.py --model-path-address model@host@port --num-gpus 2 --gpus 0,1 --max-gpu-memory 10GiB

"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from llm_api_launch import launch_all,parser,controller_args,worker_args,server_args
from api import create_app
import uvicorn

parser.add_argument("--api-host", type=str, default="0.0.0.0")
parser.add_argument("--api-port", type=int, default=7861)
parser.add_argument("--ssl_keyfile", type=str)
parser.add_argument("--ssl_certfile", type=str)
# 初始化消息
args = parser.parse_args()
args_dict = vars(args)

api_args = ["api-host","api-port","ssl_keyfile","ssl_certfile"]

def run_api(host, port, **kwargs):
    app = create_app()
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app,
                    host=host,
                    port=port,
                    ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"),
                    )
    else:
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    launch_all(args=args,controller_args=controller_args,worker_args=worker_args,server_args=server_args)
    run_api(
            host=args.api_host,
            port=args.api_port,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            )

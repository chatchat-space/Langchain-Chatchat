import sys
import os 
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs.model_config import LOG_PATH,controller_args,worker_args,server_args,parser
import subprocess
import re
import argparse

args = parser.parse_args()
# 必须要加http//:，否则InvalidSchema: No connection adapters were found
args = argparse.Namespace(**vars(args),**{"controller-address":f"http://{args.controller_host}:{str(args.controller_port)}"})

if args.gpus:
    if len(args.gpus.split(",")) < args.num_gpus:
        raise ValueError(
            f"Larger --num-gpus ({args.num_gpus}) than --gpus {args.gpus}!"
        )
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpus

# 0,controller, model_worker, openai_api_server
# 1, 命令行选项
# 2,LOG_PATH
# 3, log的文件名
base_launch_sh = "nohup python3 -m fastchat.serve.{0} {1} >{2}/{3}.log 2>&1 &" 

# 0 log_path
#! 1 log的文件名，必须与bash_launch_sh一致
# 2 controller, worker, openai_api_server
base_check_sh = """while [ `grep -c "Uvicorn running on" {0}/{1}.log` -eq '0' ];do
                        sleep 1s;
                        echo "wait {2} running"
                done
                echo '{2} running' """


def string_args(args,args_list):
    """将args中的key转化为字符串"""
    args_str = ""
    for key, value in args._get_kwargs():
        # args._get_kwargs中的key以_为分隔符,先转换，再判断是否在指定的args列表中
        key = key.replace("_","-") 
        if key not in args_list:
             continue
        # fastchat中port,host没有前缀，去除前缀
        key = key.split("-")[-1] if re.search("port|host",key) else key 
        if not value:
            pass
        # 1==True ->  True
        elif isinstance(value,bool) and value == True:
            args_str += f" --{key} "
        elif isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
            value = " ".join(value)
            args_str += f" --{key} {value} "
        else:
            args_str += f" --{key} {value} "

    return args_str

def launch_worker(item):
            log_name = item.split("/")[-1].split("\\")[-1].replace("-","_").replace("@","_").replace(".","_")
            # 先分割model-path-address,在传到string_args中分析参数
            args.model_path,args.worker_host, args.worker_port = item.split("@")
            print("*"*80)        
            worker_str_args = string_args(args,worker_args)
            print(worker_str_args)
            worker_sh = base_launch_sh.format("model_worker",worker_str_args,LOG_PATH,f"worker_{log_name}")
            worker_check_sh = base_check_sh.format(LOG_PATH,f"worker_{log_name}","model_worker")
            subprocess.run(worker_sh,shell=True,check=True)
            subprocess.run(worker_check_sh,shell=True,check=True)


def launch_all():
    controller_str_args = string_args(args,controller_args)
    controller_sh = base_launch_sh.format("controller",controller_str_args,LOG_PATH,"controller")
    controller_check_sh = base_check_sh.format(LOG_PATH,"controller","controller")
    subprocess.run(controller_sh,shell=True,check=True)
    subprocess.run(controller_check_sh,shell=True,check=True)

    if isinstance(args.model_path_address, str):
        launch_worker(args.model_path_address)
    else:
        for idx,item in enumerate(args.model_path_address):
            print(f"开始加载第{idx}个模型:{item}")
            launch_worker(item)
    
    server_str_args = string_args(args,server_args)
    server_sh = base_launch_sh.format("openai_api_server",server_str_args,LOG_PATH,"openai_api_server")
    server_check_sh = base_check_sh.format(LOG_PATH,"openai_api_server","openai_api_server")
    subprocess.run(server_sh,shell=True,check=True)
    subprocess.run(server_check_sh,shell=True,check=True)

if __name__ == "__main__":
    launch_all()
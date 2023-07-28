import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from configs.model_config import llm_model_dict, LLM_MODEL, LOG_PATH, logger


def execute_command(command):
    process = subprocess.Popen(command, shell=True)
    return process.pid


host_ip = "0.0.0.0"
port = 8887
# 1. llm_model_dict精简；

# 2. 不同任务的日志还是分开；

# 3. 在此处定义args，可选fastchat为每个服务所提供的命令行参数，model_path除外；

# 4. 用logger.removeHandler把它添加的handler删掉，添加我们自己的handler;

# 5. 用watchdog监控第二步的执行情况；

# 6. requirements指定fastchat版本号。

print(llm_model_dict[LLM_MODEL])
model_path = llm_model_dict[LLM_MODEL]["local_model_path"]
if not model_path:
    logger.error("local_model_path 不能为空")
else:
    # 启动任务
    command1 = f'nohup python -m fastchat.serve.controller >> {LOG_PATH}/controller_log.txt 2>&1 &'
    process1 = execute_command(command1)
    logger.info(f"已执行 {command1}")
    logger.info(f"Process 1 started with PID: {process1}")

    command2 = f'nohup python -m fastchat.serve.model_worker --model-path "{model_path}" --device cuda >> {LOG_PATH}/worker_log.txt 2>&1 &'
    process2 = execute_command(command2)
    logger.info(f"已执行 {command2}")
    logger.info(f"Process 2 started with PID: {process2}")

    command3 = f'nohup python -m fastchat.serve.openai_api_server --host "{host_ip}" --port {port} >> {LOG_PATH}/api_log.txt 2>&1 &'
    process3 = execute_command(command3)
    logger.info(f"已执行 {command3}")
    logger.info(f"Process 3 started with PID: {process3}")

    # TODO: model_worker.log 与 controller.log 存储位置未指定为 LOG_PATH --> （hzg0601）model_worker.py,controller.py自行指定的文件写入路径，
    # TODO(hzg0601): -->而且是写死的，如果想修改路径必须修改fastchat的代码
    logger.info(f"如需查看 llm_api 日志，请前往 {LOG_PATH}")

# 服务启动后接口调用示例：
# import openai
# openai.api_key = "EMPTY" # Not support yet
# openai.api_base = "http://0.0.0.0:8000/v1"

# model = "chatglm2-6b"

# # create a chat completion
# completion = openai.ChatCompletion.create(
#   model=model,
#   messages=[{"role": "user", "content": "Hello! What is your name?"}]
# )
# # print the completion
# print(completion.choices[0].message.content)

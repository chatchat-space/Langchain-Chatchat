
#### 项目启动选项
```test
usage: langchina-ChatGLM [-h] [--no-remote-model] [--model MODEL] [--lora LORA] [--model-dir MODEL_DIR] [--lora-dir LORA_DIR] [--cpu] [--auto-devices] [--gpu-memory GPU_MEMORY [GPU_MEMORY ...]] [--cpu-memory CPU_MEMORY]
                         [--load-in-8bit] [--bf16]

基于langchain和chatGML的LLM文档阅读器

options:
  -h, --help            show this help message and exit
  --no-remote-model     remote in the model on loader checkpoint, if your load local model to add the ` --no-remote-model`
  --model MODEL         Name of the model to load by default.
  --lora LORA           Name of the LoRA to apply to the model by default.
  --model-dir MODEL_DIR
                        Path to directory with all the models
  --lora-dir LORA_DIR   Path to directory with all the loras
  --cpu                 Use the CPU to generate text. Warning: Training on CPU is extremely slow.
  --auto-devices        Automatically split the model across the available GPU(s) and CPU.
  --gpu-memory GPU_MEMORY [GPU_MEMORY ...]
                        Maxmimum GPU memory in GiB to be allocated per GPU. Example: --gpu-memory 10 for a single GPU, --gpu-memory 10 5 for two GPUs. You can also set values in MiB like --gpu-memory 3500MiB.
  --cpu-memory CPU_MEMORY
                        Maximum CPU memory in GiB to allocate for offloaded weights. Same as above.
  --load-in-8bit        Load the model with 8-bit precision.
  --bf16                Load the model with bfloat16 precision. Requires NVIDIA Ampere GPU.

```

#### 示例

- 1、加载本地模型

```text
--model-dir 本地checkpoint存放文件夹
--model  模型名称
--no-remote-model 不从远程加载模型
```
```shell
$  python cli_demo.py --model-dir /media/mnt/ --model chatglm-6b --no-remote-model
```

- 2、低精度加载模型
```text
--model-dir 本地checkpoint存放文件夹
--model  模型名称
--no-remote-model 不从远程加载模型
--load-in-8bit   以8位精度加载模型
```
```shell
$ python cli_demo.py --model-dir /media/mnt/ --model chatglm-6b --no-remote-model --load-in-8bit   
```


- 3、使用cpu预测模型
```text
--model-dir 本地checkpoint存放文件夹
--model  模型名称
--no-remote-model 不从远程加载模型
--cpu   使用CPU生成文本。警告：CPU上的训练非常缓慢。
```
```shell
$ python cli_demo.py --model-dir /media/mnt/ --model chatglm-6b --no-remote-model --cpu 
```



- 3、加载lora微调文件
```text
--model-dir 本地checkpoint存放文件夹
--model  模型名称
--no-remote-model 不从远程加载模型
--lora-dir   本地lora存放文件夹
--lora lora名称
```
```shell
$ python cli_demo.py --model-dir /media/mnt/ --model chatglm-6b --no-remote-model --lora-dir  /media/mnt/loras --lora chatglm-step100
```

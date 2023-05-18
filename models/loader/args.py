import argparse
import os



# Additional argparse types
def path(string):
    if not string:
        return ''
    s = os.path.expanduser(string)
    if not os.path.exists(s):
        raise argparse.ArgumentTypeError(f'No such file or directory: "{string}"')
    return s


def file_path(string):
    if not string:
        return ''
    s = os.path.expanduser(string)
    if not os.path.isfile(s):
        raise argparse.ArgumentTypeError(f'No such file: "{string}"')
    return s


def dir_path(string):
    if not string:
        return ''
    s = os.path.expanduser(string)
    if not os.path.isdir(s):
        raise argparse.ArgumentTypeError(f'No such directory: "{string}"')
    return s


parser = argparse.ArgumentParser(prog='langchina-ChatGLM',
                                 description='基于langchain和chatGML的LLM文档阅读器')



parser.add_argument('--no-remote-model',  action='store_true', default=False,  help='remote in the model on loader checkpoint, if your load local model to add the ` --no-remote-model`')
parser.add_argument('--model', type=str, default='chatglm-6b', help='Name of the model to load by default.')
parser.add_argument('--lora', type=str, help='Name of the LoRA to apply to the model by default.')
parser.add_argument("--model-dir", type=str, default='model/', help="Path to directory with all the models")
parser.add_argument("--lora-dir", type=str, default='loras/', help="Path to directory with all the loras")

# Accelerate/transformers
parser.add_argument('--cpu', action='store_true', help='Use the CPU to generate text. Warning: Training on CPU is extremely slow.')
parser.add_argument('--auto-devices', action='store_true', help='Automatically split the model across the available GPU(s) and CPU.')
parser.add_argument('--gpu-memory', type=str, nargs="+", help='Maxmimum GPU memory in GiB to be allocated per GPU. Example: --gpu-memory 10 for a single GPU, --gpu-memory 10 5 for two GPUs. You can also set values in MiB like --gpu-memory 3500MiB.')
parser.add_argument('--cpu-memory', type=str, help='Maximum CPU memory in GiB to allocate for offloaded weights. Same as above.')
parser.add_argument('--load-in-8bit', action='store_true', help='Load the model with 8-bit precision.')
parser.add_argument('--bf16', action='store_true', help='Load the model with bfloat16 precision. Requires NVIDIA Ampere GPU.')


args = parser.parse_args([])
# Generares dict with a default value for each argument
DEFAULT_ARGS = vars(args)




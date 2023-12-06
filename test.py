from transformers import FuyuProcessor, FuyuForCausalLM
from PIL import Image
import requests
import torch

# 加载模型和处理器
model_id = "/data/models/fuyu-8b"
processor = FuyuProcessor.from_pretrained(model_id)
model = FuyuForCausalLM.from_pretrained(model_id, device_map="cuda:0", torch_dtype=torch.float16)

# 将模型转换为 bf16
model = model.to(dtype=torch.bfloat16)

# 准备模型的输入
# text_prompt = "According to this chart, which model performs best?\n"

text_prompt = "Generate a coco-style caption.\n"
image = Image.open("1.png").convert("RGB")

while True:
    # 获取用户输入的文本提示
    text_prompt = input("请输入文本提示: ")
    if text_prompt.lower() == 'exit':
        break
    inputs = processor(text=text_prompt, images=image, return_tensors="pt").to("cuda:0")

    # 生成输出
    generation_output = model.generate(**inputs, max_new_tokens=7)
    generation_text = processor.batch_decode(generation_output[:, -7:], skip_special_tokens=True)

    # 打印生成的文本
    print(generation_text)

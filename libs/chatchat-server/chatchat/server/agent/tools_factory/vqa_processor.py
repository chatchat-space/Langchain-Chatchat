"""
Method Use cogagent to generate response for a given image and query.
"""
import base64
import re
from io import BytesIO

from PIL import Image, ImageDraw

from chatchat.server.agent.container import container
from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

from .tools_registry import BaseToolOutput, regist_tool


def extract_between_markers(text, start_marker, end_marker):
    """
    Extracts and returns the portion of the text that is between 'start_marker' and 'end_marker'.
    """
    start = text.find(start_marker)
    end = text.find(end_marker, start)

    if start != -1 and end != -1:
        # Extract and return the text between the markers, without including the markers themselves
        return text[start + len(start_marker) : end].strip()
    else:
        return "Text not found between the specified markers"


def draw_box_on_existing_image(base64_image, text):
    """
    在已有的Base64编码的图片上根据“Grounded Operation”中的坐标信息绘制矩形框。
    假设坐标是经过缩放的比例坐标。
    """
    # 解码并打开Base64编码的图片
    img = Image.open(BytesIO(base64.b64decode(base64_image)))
    draw = ImageDraw.Draw(img)

    # 提取“Grounded Operation”后的坐标
    pattern = r"\[\[(\d+),(\d+),(\d+),(\d+)\]\]"
    match = re.search(pattern, text)
    if not match:
        return None

    coords = tuple(map(int, match.groups()))
    scaled_coords = (
        int(coords[0] * 0.001 * img.width),
        int(coords[1] * 0.001 * img.height),
        int(coords[2] * 0.001 * img.width),
        int(coords[3] * 0.001 * img.height),
    )
    draw.rectangle(scaled_coords, outline="red", width=3)

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img.save("tmp/image.jpg")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    return img_base64


def vqa_run(
    model,
    tokenizer,
    image_base_64,
    query,
    history=[],
    device="cuda",
    max_length=2048,
    top_p=0.9,
    temperature=1.0,
):
    """
    Args:
        image_path (str): path to the image
        query (str): query
        model (torch.nn.Module): model
        history (list): history
        image (torch.Tensor): image
        max_length (int): max length
        top_p (float): top p
        temperature (float): temperature
        top_k (int): top k
    """
    import torch

    image = Image.open(BytesIO(base64.b64decode(image_base_64)))

    inputs = model.build_conversation_input_ids(
        tokenizer, query=query, history=history, images=[image]
    )
    inputs = {
        "input_ids": inputs["input_ids"].unsqueeze(0).to(device),
        "token_type_ids": inputs["token_type_ids"].unsqueeze(0).to(device),
        "attention_mask": inputs["attention_mask"].unsqueeze(0).to(device),
        "images": [[inputs["images"][0].to(device).to(torch.bfloat16)]],
        "cross_images": [[inputs["cross_images"][0].to(device).to(torch.bfloat16)]]
        if inputs["cross_images"]
        else None,
    }

    gen_kwargs = {
        "max_length": max_length,
        # "temperature": temperature,
        "top_p": top_p,
        "do_sample": False,
    }
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs["input_ids"].shape[1] :]
        response = tokenizer.decode(outputs[0])
        response = response.split("</s>")[0]

    return response


@regist_tool(title="图片对话")
def vqa_processor(
    query: str = Field(description="The question of the image in English"),
):
    """use this tool to get answer for image question"""

    tool_config = get_tool_config("vqa_processor")
    if container.metadata["images"]:
        image_base64 = container.metadata["images"][0]
        ans = vqa_run(
            model=container.vision_model,
            tokenizer=container.vision_tokenizer,
            query=query + "(with grounding)",
            image_base_64=image_base64,
            device=tool_config["device"],
        )
        print(ans)
        image_new_base64 = draw_box_on_existing_image(
            container.metadata["images"][0], ans
        )

        # Markers
        # start_marker = "Next Action:draw_box_on_existing_image
        # end_marker = "Grounded Operation:"
        # ans = extract_between_markers(ans, start_marker, end_marker)

        ret = ans
    else:
        ret = "No Image, Please Try Again"

    return BaseToolOutput(ret)

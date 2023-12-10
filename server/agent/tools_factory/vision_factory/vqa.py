"""
Method Use cogagent to generate response for a given image and query.
"""
import base64
from io import BytesIO
import torch
from PIL import Image
from pydantic import BaseModel, Field
from configs import TOOL_CONFIG

def vqa_run(model, tokenizer, image_base_64, query, history=[], device="cuda", max_length=2048, top_p=0.9,
            temperature=1.0):
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
    image = Image.open(BytesIO(base64.b64decode(image_base_64)))

    inputs = model.build_conversation_input_ids(tokenizer, query=query, history=history, images=[image])
    inputs = {
        'input_ids': inputs['input_ids'].unsqueeze(0).to(device),
        'token_type_ids': inputs['token_type_ids'].unsqueeze(0).to(device),
        'attention_mask': inputs['attention_mask'].unsqueeze(0).to(device),
        'images': [[inputs['images'][0].to(device).to(torch.bfloat16)]],
        'cross_images': [[inputs['cross_images'][0].to(device).to(torch.bfloat16)]] if inputs[
            'cross_images'] else None,
    }
    gen_kwargs = {"max_length": max_length,
                  "temperature": temperature,
                  "top_p": top_p,
                  "do_sample": False}
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0])
        response = response.split("</s>")[0]

    return response


def vqa_processor(query: str):
    from server.agent.container import container
    tool_config = TOOL_CONFIG["vqa_processor"]
    # model, tokenizer = load_model(model_path=tool_config["model_path"],
    #                               tokenizer_path=tool_config["tokenizer_path"],
    #                               device=tool_config["device"])
    if container.metadata["images"]:
        image_base64 = container.metadata["images"][0]
        return vqa_run(model=container.vision_model, tokenizer=container.vision_tokenizer, query=query, image_base_64=image_base64,
                       device=tool_config["device"])
    else:
        return "No Image, Please Try Again"


class VQAInput(BaseModel):
    query: str = Field(description="The question of the image in English")

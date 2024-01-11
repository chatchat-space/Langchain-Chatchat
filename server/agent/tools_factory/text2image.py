from PIL import Image
from typing import List

from langchain.agents import tool
from langchain.pydantic_v1 import Field
import openai


def get_image_model_config() -> dict:
    from configs.model_config import LLM_MODEL_CONFIG, ONLINE_LLM_MODEL

    model = LLM_MODEL_CONFIG.get("image_model")
    if model:
        name = list(model.keys())[0]
        if config := ONLINE_LLM_MODEL.get(name):
            config = {**list(model.values())[0], **config}
            config.setdefault("model_name", name)
            return config


@tool
def text2images(
    prompt: str,
    n: int = Field(1, description="需生成图片的数量"),
    width: int = Field(512, description="生成图片的宽度"),
    height: int = Field(512, description="生成图片的高度"),
) -> List[str]:
    '''根据用户的描述生成图片'''
    model_config = get_image_model_config()
    assert model_config is not None, "请正确配置文生图模型"

    client = openai.Client(
        base_url=model_config["api_base_url"],
        api_key=model_config["api_key"],
        timeout=600,
    )
    resp = client.images.generate(prompt=prompt,
                                  n=n,
                                  size=f"{width}*{height}",
                                  response_format="url",
                                  model=model_config["model_name"],
                                  )
    return [x.url for x in resp.data]


if __name__ == "__main__":
    from matplotlib import pyplot as plt
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))

    prompt = "draw a house with trees and river"
    prompt = "画一个带树、草、河流的山中小屋"
    params = text2images.args_schema.parse_obj({"prompt": prompt}).dict()
    print(params)
    image = text2images.invoke(params)[0]
    plt.imshow(image)
    plt.show()

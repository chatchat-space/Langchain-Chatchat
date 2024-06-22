import base64
import json
import os
import uuid
from typing import List

import openai
from PIL import Image

from chatchat.configs import MEDIA_PATH
from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import MsgType, get_tool_config

from .tools_registry import BaseToolOutput, regist_tool


def get_image_model_config() -> dict:
    # from chatchat.configs import LLM_MODEL_CONFIG, ONLINE_LLM_MODEL
    # TODO ONLINE_LLM_MODEL的配置被删除，此处业务需要修改
    # model = LLM_MODEL_CONFIG.get("image_model")
    # if model:
    #     name = list(model.keys())[0]
    #     if config := ONLINE_LLM_MODEL.get(name):
    #         config = {**list(model.values())[0], **config}
    #         config.setdefault("model_name", name)
    #         return config
    pass


@regist_tool(title="文生图", return_direct=True)
def text2images(
    prompt: str,
    n: int = Field(1, description="需生成图片的数量"),
    width: int = Field(512, description="生成图片的宽度"),
    height: int = Field(512, description="生成图片的高度"),
) -> List[str]:
    """根据用户的描述生成图片"""

    model_config = get_image_model_config()
    assert model_config is not None, "请正确配置文生图模型"

    client = openai.Client(
        base_url=model_config["api_base_url"],
        api_key=model_config["api_key"],
        timeout=600,
    )
    resp = client.images.generate(
        prompt=prompt,
        n=n,
        size=f"{width}*{height}",
        response_format="b64_json",
        model=model_config["model_name"],
    )
    images = []
    for x in resp.data:
        uid = uuid.uuid4().hex
        filename = f"image/{uid}.png"
        with open(os.path.join(MEDIA_PATH, filename), "wb") as fp:
            fp.write(base64.b64decode(x.b64_json))
        images.append(filename)
    return BaseToolOutput(
        {"message_type": MsgType.IMAGE, "images": images}, format="json"
    )


if __name__ == "__main__":
    import sys
    from io import BytesIO
    from pathlib import Path

    from matplotlib import pyplot as plt

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))

    prompt = "draw a house with trees and river"
    prompt = "画一个带树、草、河流的山中小屋"
    params = text2images.args_schema.parse_obj({"prompt": prompt}).dict()
    print(params)
    image = text2images.invoke(params)[0]
    buffer = BytesIO(base64.b64decode(image))
    image = Image.open(buffer)
    plt.imshow(image)
    plt.show()

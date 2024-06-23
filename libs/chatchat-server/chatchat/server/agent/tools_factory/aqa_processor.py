import base64

from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

from .tools_registry import BaseToolOutput, regist_tool


def save_base64_audio(base64_audio, file_path):
    audio_data = base64.b64decode(base64_audio)
    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_data)


def aqa_run(model, tokenizer, query):
    query = tokenizer.from_list_format([query])
    response, history = model.chat(tokenizer, query=query, history=None)
    print(response)
    return response


@regist_tool(title="音频问答")
def aqa_processor(
    query: str = Field(description="The question of the audio in English"),
):
    """use this tool to get answer for audio question"""

    from chatchat.server.agent.container import container

    if container.metadata["audios"]:
        file_path = "temp_audio.mp3"
        save_base64_audio(container.metadata["audios"][0], file_path)
        query_input = {
            "audio": file_path,
            "text": query,
        }
        ret = aqa_run(
            tokenizer=container.audio_tokenizer,
            query=query_input,
            model=container.audio_model,
        )
    else:
        ret = "No Audio, Please Try Again"

    return BaseToolOutput(ret)

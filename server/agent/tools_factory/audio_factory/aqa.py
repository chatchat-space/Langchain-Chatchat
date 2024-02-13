import base64
import os
from langchain.pydantic_v1 import BaseModel, Field

def save_base64_audio(base64_audio, file_path):
    audio_data = base64.b64decode(base64_audio)
    with open(file_path, 'wb') as audio_file:
        audio_file.write(audio_data)

def aqa_run(model, tokenizer, query):
    query = tokenizer.from_list_format([query])
    response, history = model.chat(tokenizer, query=query, history=None)
    print(response)
    return response


def aqa_processor(query: str):
    from server.agent.container import container
    if container.metadata["audios"]:
        file_path = "temp_audio.mp3"
        save_base64_audio(container.metadata["audios"][0], file_path)
        query_input = {
            "audio": file_path,
            "text": query,
        }
        return aqa_run(tokenizer=container.audio_tokenizer, query=query_input, model=container.audio_model)
    else:
        return "No Audio, Please Try Again"

class AQAInput(BaseModel):
    query: str = Field(description="The question of the image in English")

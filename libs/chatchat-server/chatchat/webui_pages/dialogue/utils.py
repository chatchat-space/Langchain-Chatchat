import base64
import os
from io import BytesIO

import streamlit as st


def encode_file_to_base64(file):
    # 将文件内容转换为 Base64 编码
    buffer = BytesIO()
    buffer.write(file.read())
    return base64.b64encode(buffer.getvalue()).decode()


def process_files(files):
    result = {"videos": [], "images": [], "audios": []}
    for file in files:
        file_extension = os.path.splitext(file.name)[1].lower()

        # 检测文件类型并进行相应的处理
        if file_extension in [".mp4", ".avi"]:
            # 视频文件处理
            video_base64 = encode_file_to_base64(file)
            result["videos"].append(video_base64)
        elif file_extension in [".jpg", ".png", ".jpeg"]:
            # 图像文件处理
            image_base64 = encode_file_to_base64(file)
            result["images"].append(image_base64)
        elif file_extension in [".mp3", ".wav", ".ogg", ".flac"]:
            # 音频文件处理
            audio_base64 = encode_file_to_base64(file)
            result["audios"].append(audio_base64)

    return result

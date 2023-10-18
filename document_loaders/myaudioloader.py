from typing import List
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from langchain.document_loaders.unstructured import UnstructuredFileLoader
import numpy as np
import subprocess
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Ifasr import RequestApi,get_transcript_from_lattice

API = True
audio_model = "damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
model_revision="v1.2.4"
appid = "00853967"
secret_key = "4fcabeb7dbc584a4c80f180d96a2be84"
def get_audio_from_path(filepath):
    # 获取文件扩展名
    ext = os.path.splitext(filepath)[1].lower()

    supported_formats = ['.wav', '.pcm', '.mp3', '.m4a', '.aac', '.ogg', '.opus', '.flac', '.wma', '.ape', '.tta']

    if ext in supported_formats:
        cmd = [
            'ffmpeg', 
            '-i', filepath,
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',  # 将采样率设置为 16kHz
            '-ac', '1',  # 将音频设置为单声道
            '-'
        ]
        audio = np.frombuffer(subprocess.check_output(cmd), dtype=np.int16)
        return audio
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

class AudioLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        def audio2text(filepath):
            if not API:
                audio = get_audio_from_path(filepath)
                audio = audio.astype(np.float32)
                inference_pipeline = pipeline(
                    task=Tasks.auto_speech_recognition,
                    model=audio_model,
                    model_revision=model_revision)
                rec_result = inference_pipeline(audio_in=audio)
                return rec_result['text']
            else:
                api = RequestApi(appid=appid,
                                secret_key=secret_key,
                                upload_file_path=filepath)

                result = api.get_result()
                text = get_transcript_from_lattice(result['content']['orderResult'])
                return text

        text = audio2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    loader = AudioLoader(file_path="../tests/samples/wav_test.wav")
    docs = loader.load()
    print(docs)

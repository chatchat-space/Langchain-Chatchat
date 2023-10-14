from typing import List
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from langchain.document_loaders.unstructured import UnstructuredFileLoader
import numpy as np
import subprocess
import os

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
            audio = get_audio_from_path(filepath)
            audio = audio.astype(np.float32)
            inference_pipeline = pipeline(
                task=Tasks.auto_speech_recognition,
                model='damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
                model_revision="v1.2.4")
            rec_result = inference_pipeline(audio_in=audio)
            return rec_result['text']

        text = audio2text(self.file_path)
        from unstructured.partition.text import partition_text
        return partition_text(text=text, **self.unstructured_kwargs)


if __name__ == "__main__":
    loader = AudioLoader(file_path="../tests/samples/wav_test.wav")
    docs = loader.load()
    print(docs)

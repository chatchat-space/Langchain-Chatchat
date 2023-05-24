FROM python:3.8

MAINTAINER "chatGLM"


RUN pip install --user torch torchvision tensorboard cython -i https://pypi.tuna.tsinghua.edu.cn/simple
# RUN pip install --user 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

# RUN pip install --user 'git+https://github.com/facebookresearch/fvcore'
# install detectron2
# RUN git clone https://github.com/facebookresearch/detectron2

WORKDIR /chatGLM

COPY requirements.txt /chatGLM/

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

COPY agent /chatGLM/agent

COPY chains /chatGLM/chains

COPY configs /chatGLM/configs

COPY content /chatGLM/content

COPY models /chatGLM/models

COPY nltk_data /chatGLM/content

COPY cli_demo.py /chatGLM/

COPY textsplitter /chatGLM/textsplitter

COPY webui.py /chatGLM/

COPY utils /chatGLM/utils

CMD ["python","-u", "webui.py"]

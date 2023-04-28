FROM python:3.8

MAINTAINER "chatGLM"

RUN useradd -m chatglm
WORKDIR /home/chatglm

Add . /home/chatglm

RUN pip install --user torch torchvision tensorboard cython -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

CMD ["python","-u", "webui.py"]

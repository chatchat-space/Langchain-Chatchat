# 基础镜像
FROM python:3.11
LABEL maintainer=Langchain-Chatchat
WORKDIR /root
# 环境变量
ENV CHATCHAT_ROOT=/root/chatchat_data
ENV RELEASE=0.3.1.1

# 初始化环境
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
RUN apt-get update -y && \
    apt-get install -y git && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip setuptools
RUN #pip install --index-url https://pypi.python.org/simple/ pipx && pipx install poetry --force
# Add poetry to PATH
#ENV PATH="/root/.local/bin:${PATH}"

# 下载 Langchain-Chatchat
RUN #git clone https://github.com/chatchat-space/Langchain-Chatchat.git
RUN pip install --index-url https://pypi.python.org/simple/ "langchain-chatchat[xinference]"==$RELEASE -U

#WORKDIR /root/Langchain-Chatchat/libs/chatchat-server

# 设置 poetry 官方源
#RUN poetry config virtualenvs.create false && \
#    poetry config repositories.pypi.url https://pypi.org/simple/

# 安装依赖
RUN #poetry install --with lint,test -E xinference

# 初始化配置
RUN #python cli.py init
RUN chatchat init

# Install ModelProvider
#RUN pip install xinference-client

# 将监听 IP 从 localhost 统一改为 0.0.0.0
RUN sed -i 's/127.0.0.1/0.0.0.0/g' $CHATCHAT_ROOT/basic_settings.yaml

# 初始化知识库文件
ADD /docker/data.tar.gz $CHATCHAT_ROOT/

WORKDIR $CHATCHAT_ROOT

EXPOSE 7861 8501

#ENTRYPOINT ["python", "cli.py", "start", "-a"]
ENTRYPOINT ["chatchat", "start", "-a"]
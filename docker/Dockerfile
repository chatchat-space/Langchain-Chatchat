# Base Image
FROM python:3.11
# Labels
LABEL maintainer=chatchat
# Environment Variables
ENV HOME=/usr/local/lib/python3.11/site-packages/chatchat
# Commands
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 jq && \
    apt-get clean && \
    pip install openpyxl networkx && \
    rm -rf /var/lib/apt/lists/*
# 安装需要的包
RUN pip install langchain-chatchat[xinference] -U
# 进行自定义设置
RUN chatchat-config server --default_bind_host=0.0.0.0
# 拷贝自定义配置文件和数据文件
COPY /libs/chatchat-server/chatchat/configs/model_providers.yaml $HOME/configs/model_providers.yaml
COPY /libs/chatchat-server/chatchat/data $HOME/data
WORKDIR $HOME
EXPOSE 7861 8501
ENTRYPOINT ["chatchat", "-a"]
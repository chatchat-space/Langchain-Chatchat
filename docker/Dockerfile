# Base Image
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Labels
LABEL maintainer=chatchat

# Environment Variables
ENV llmname=chatglm3-6b

# Commands
WORKDIR /
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends python3.11 python3-pip curl libgl1 libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/bin/python3 && \
    ln -s /usr/bin/python3.11 /usr/bin/python3

# Copy the application files
COPY ../chatglm3-6b /data/model/chatglm3-6b
COPY ../bge-large-zh-v1.5 /data/model/bge-large-zh-v1.5
COPY ../Langchain-Chatchat /data/model/langchain-chatchat

# Install dependencies from requirements.txt
RUN pip3 install -r /data/model/langchain-chatchat/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN python3 /data/model/langchain-chatchat/init_database.py --recreate-vs
EXPOSE 22 7861 8501
WORKDIR /data/model/langchain-chatchat
ENTRYPOINT ["python3", "/data/model/langchain-chatchat/startup.py", "-a"]




## Base Image
#FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
#
## Labels
#LABEL maintainer=chatchat
#
## Environment Variables
#ENV llmname=chatglm3-6b
#
## Commands
#WORKDIR /
#RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone
#RUN apt-get update -y
#RUN apt-get install -y python3.11 python3-pip
#RUN apt-get install -y curl libgl1 libglib2.0-0
#RUN apt-get clean
#
#RUN rm -f /usr/bin/python3 && ln -s /usr/bin/python3.11 /usr/bin/python3
#
## 判断Python版本是否为3.11
##RUN python3 -V > python_version.txt
##RUN echo "Current Python version is $(cat python_version.txt)" && \
##    if grep -q "Python 3.11" python_version.txt; then \
##    echo "Python version is 3.11"; \
##    else \
##    echo "Python version is not 3.11" && exit 1; \
##    fi
#
## Copy the application files
##COPY ~/zh_core_web_lg-3.6.0-py3-none-any.whl /zh_core_web_lg-3.6.0-py3-none-any.whl
##RUN pip3 install /zh_core_web_lg-3.6.0-py3-none-any.whl -i https://pypi.tuna.tsinghua.edu.cn/simple
#COPY ./chatglm3-6b /data/model/chatglm3-6b
#COPY ./bge-large-zh-v1.5 /data/model/bge-large-zh-v1.5
##COPY ~/text2vec-bge-large-chinese /text2vec-bge-large-chinese
#COPY ./Langchain-Chatchat-0.2.10 /data/model/langchain-chatchat
#
## Install dependencies from requirements.txt
#RUN pip3 install -r /data/model/langchain-chatchat/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
#
##RUN mkdir /root/nltk_data
##COPY ./Langchain-Chatchat-0.2.10/nltk_data/ /root/nltk_data/
##RUN mkdir /logs
##COPY ./start_service.sh /langchain-chatchat
#RUN python3 /data/model/langchain-chatchat/init_database.py --recreate-vs
#EXPOSE 22 7861 8501
#WORKDIR /data/model/langchain-chatchat
##ENTRYPOINT ["bash", "-il", "start_service.sh"]
#ENTRYPOINT ["python3", "/data/model/langchain-chatchat/startup.py", "-a"]
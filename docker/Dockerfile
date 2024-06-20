# Base Image
FROM python:3.11
# Labels
LABEL maintainer=chatchat
# Environment Variables
ENV HOME=/usr/local/lib/python3.11/site-packages/chatchat
# Init Environment
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 jq && \
    apt-get clean && \
    pip install openpyxl networkx && \
    rm -rf /var/lib/apt/lists/*
# Install Chatchat
RUN pip install langchain-chatchat[xinference] -U
# Make Custom Settings
RUN chatchat-config server --default_bind_host=0.0.0.0
# Copy Custom Files
COPY /libs/chatchat-server/chatchat/configs/model_providers.yaml $HOME/configs/model_providers.yaml
COPY /libs/chatchat-server/chatchat/data $HOME/data
WORKDIR $HOME
EXPOSE 7861 8501
ENTRYPOINT ["chatchat", "-a"]
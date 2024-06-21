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
RUN pip install langchain-chatchat -U
# Install ModelPlatform
RUN pip install xinference-client
RUN pip install streamlit-chatbox==1.1.12.post4
# Make Custom Settings
RUN chatchat-config server --default_bind_host=0.0.0.0
RUN chatchat-kb -r
# Copy Custom Files
COPY /libs/chatchat-server/chatchat/configs/model_providers.yaml $HOME/configs/model_providers.yaml
COPY /libs/chatchat-server/chatchat/data $HOME/data
WORKDIR $HOME
EXPOSE 7861 8501
ENTRYPOINT ["chatchat", "-a"]
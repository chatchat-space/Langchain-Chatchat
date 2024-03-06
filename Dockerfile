FROM python:3.11

RUN apt-get update
RUN apt-get install -y libgl1-mesa-glx

RUN mkdir /Langchain-Chatchat
COPY requirements.txt /Langchain-Chatchat
COPY requirements_api.txt /Langchain-Chatchat
COPY requirements_webui.txt /Langchain-Chatchat

WORKDIR /Langchain-Chatchat
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements_api.txt
RUN pip install -r requirements_webui.txt

EXPOSE 8501
EXPOSE 7861
EXPOSE 20000

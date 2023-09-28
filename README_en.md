![](img/logo-long-chatchat-trans-v2.png)

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white "langchain-chatglm")](https://t.me/+RjliQ3jnJ1YyN2E9)

🌍 [中文文档](README.md)

📃 **LangChain-Chatchat** (formerly Langchain-ChatGLM):  A LLM application aims to implement knowledge and search engine based QA based on Langchain and open-source or remote LLM API.

## Content

* [Introduction](README_en.md#Introduction)
* [Change Log](README_en.md#Change-Log)
* [Supported Models](README_en.md#Supported-Models)
* [Docker Deployment](README_en.md#Docker-Deployment)
* [Development](README_en.md#Development)
  * [Environment Prerequisite](README_en.md#Environment-Prerequisite)
  * [Preparing Deployment Environment](README_en.md#1.-Preparing-Deployment-Environment)
  * [Downloading model to local disk](README_en.md#2.-Downloading-model-to-local-disk)
  * [Setting Configuration](README_en.md#3.-Setting-Configuration)
  * [Knowledge Base Migration](README_en.md#4.-Knowledge-Base-Migration)
  * [Launching API Service or WebUI](README_en.md#5.-Launching-API-Service-or-WebUI-with-One-Command)
* [FAQ](README_en.md#FAQ)
* [Roadmap](README_en.md#Roadmap)

---

## Introduction

🤖️ A Q&A application based on local knowledge base implemented using the idea of [langchain](https://github.com/hwchase17/langchain). The goal is to build a KBQA(Knowledge based Q&A) solution that is friendly to Chinese scenarios and open source models and can run both offline and online.

💡 Inspried by [document.ai](https://github.com/GanymedeNil/document.ai)  and [ChatGLM-6B Pull Request](https://github.com/THUDM/ChatGLM-6B/pull/216) , we build a local knowledge base question answering application that can be implemented using an open source model  or remote LLM api throughout the process. In the latest version of this project, [FastChat](https://github.com/lm-sys/FastChat) is used to access Vicuna, Alpaca, LLaMA, Koala, RWKV and many other models. Relying on [langchain](https:// github.com/langchain-ai/langchain) , this project supports calling services through the API provided based on [FastAPI](https://github.com/tiangolo/fastapi), or using the WebUI based on [Streamlit](https://github.com /streamlit/streamlit) .

✅ Relying on the open source LLM and Embedding models, this project can realize full-process **offline private deployment**. At the same time, this project also supports the call of OpenAI GPT API- and Zhipu API, and will continue to expand the access to various models and remote APIs in the future.

⛓️ The implementation principle of this project is shown in the graph below. The main process includes: loading files -> reading text -> text segmentation -> text vectorization -> question vectorization -> matching the `top-k` most similar to the question vector in the text vector -> The matched text is added to `prompt `as context and question -> submitted to `LLM` to generate an answer.

📺[video introdution](https://www.bilibili.com/video/BV13M4y1e7cN/?share_source=copy_web&vd_source=e6c5aafe684f30fbe41925d61ca6d514)

![实现原理图](img/langchain+chatglm.png)

The main process analysis from the aspect of document process:

![实现原理图2](img/langchain+chatglm2.png)

🚩 The training or fined-tuning are not involved in the project, but still, one always can improve performance by do these.

🌐 [AutoDL image](registry.cn-beijing.aliyuncs.com/chatchat/chatchat:0.2.0) is supported, and in v7 the codes are update to v0.2.3.

🐳 [Docker image](registry.cn-beijing.aliyuncs.com/chatchat/chatchat:0.2.0)

💻 Run Docker with one command:

```shell
docker run -d --gpus all -p 80:8501 registry.cn-beijing.aliyuncs.com/chatchat/chatchat:0.2.0
```

---

## Environment Minimum Requirements

To run this code smoothly, please configure it according to the following minimum requirements:
+ Python version: >= 3.8.5, < 3.11
+ Cuda version: >= 11.7, with Python installed.

If you want to run the native model (int4 version) on the GPU without problems, you need at least the following hardware configuration.

+ chatglm2-6b & LLaMA-7B Minimum RAM requirement: 7GB Recommended graphics cards: RTX 3060, RTX 2060
+ LLaMA-13B Minimum graphics memory requirement: 11GB Recommended cards: RTX 2060 12GB, RTX3060 12GB, RTX3080, RTXA2000 
+ Qwen-14B-Chat Minimum memory requirement: 13GB Recommended graphics card: RTX 3090
+ LLaMA-30B Minimum Memory Requirement: 22GB Recommended Cards: RTX A5000,RTX 3090,RTX 4090,RTX 6000,Tesla V100,RTX Tesla P40 
+ Minimum memory requirement for LLaMA-65B: 40GB Recommended cards: A100,A40,A6000

If int8 then memory x1.5 fp16 x2.5 requirement.
For example: using fp16 to reason about the Qwen-7B-Chat model requires 16GB of video memory.

The above is only an estimate, the actual situation is based on nvidia-smi occupancy.

## Change Log

plese refer to [version change log](https://github.com/imClumsyPanda/langchain-ChatGLM/releases)

### Current Features

* **Consistent LLM Service based on FastChat**. The project use [FastChat](https://github.com/lm-sys/FastChat) to provide the API service of the open source LLM models and access it in the form of OpenAI API interface to improve the loading effect of the LLM model;
* **Chain and Agent based on Langchian**. Use the existing Chain implementation in [langchain](https://github.com/langchain-ai/langchain) to facilitate subsequent access to different types of Chain, and will test Agent access;
* **Full fuction API service based on FastAPI**. All interfaces can be tested in the docs automatically generated by [FastAPI](https://github.com/tiangolo/fastapi), and all dialogue interfaces support streaming or non-streaming output through parameters. ;
* **WebUI service based on Streamlit**. With [Streamlit](https://github.com/streamlit/streamlit), you can choose whether to start WebUI based on API services, add session management, customize session themes and switch, and will support different display of content forms of output in the future;
* **Abundant open source LLM and Embedding models**. The default LLM model in the project is changed to [THUDM/chatglm2-6b](https://huggingface.co/THUDM/chatglm2-6b), and the default Embedding model is changed to [moka-ai/m3e-base](https:// huggingface.co/moka-ai/m3e-base), the file loading method and the paragraph division method have also been adjusted. In the future, context expansion will be re-implemented and optional settings will be added;
* **Multiply vector libraries**. The project has expanded support for different types of vector libraries. Including [FAISS](https://github.com/facebookresearch/faiss), [Milvus](https://github.com/milvus -io/milvus), and [PGVector](https://github.com/pgvector/pgvector);
* **Varied Search engines**. We provide two search engines now: Bing and DuckDuckGo. DuckDuckGo search does not require configuring an API Key and can be used directly in environments with access to foreign services.

## Supported Models

The default LLM model in the project is changed to [THUDM/chatglm2-6b](https://huggingface.co/THUDM/chatglm2-6b), and the default Embedding model is changed to [moka-ai/m3e-base](https:// huggingface.co/moka-ai/m3e-base).

### Supported LLM models

The project use [FastChat](https://github.com/lm-sys/FastChat) to provide the API service of the open source LLM models, supported models include:

- [meta-llama/Llama-2-7b-chat-hf](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)
- Vicuna, Alpaca, LLaMA, Koala
- [BlinkDL/RWKV-4-Raven](https://huggingface.co/BlinkDL/rwkv-4-raven)
- [camel-ai/CAMEL-13B-Combined-Data](https://huggingface.co/camel-ai/CAMEL-13B-Combined-Data)
- [databricks/dolly-v2-12b](https://huggingface.co/databricks/dolly-v2-12b)
- [FreedomIntelligence/phoenix-inst-chat-7b](https://huggingface.co/FreedomIntelligence/phoenix-inst-chat-7b)
- [h2oai/h2ogpt-gm-oasst1-en-2048-open-llama-7b](https://huggingface.co/h2oai/h2ogpt-gm-oasst1-en-2048-open-llama-7b)
- [lcw99/polyglot-ko-12.8b-chang-instruct-chat](https://huggingface.co/lcw99/polyglot-ko-12.8b-chang-instruct-chat)
- [lmsys/fastchat-t5-3b-v1.0](https://huggingface.co/lmsys/fastchat-t5)
- [mosaicml/mpt-7b-chat](https://huggingface.co/mosaicml/mpt-7b-chat)
- [Neutralzz/BiLLa-7B-SFT](https://huggingface.co/Neutralzz/BiLLa-7B-SFT)
- [nomic-ai/gpt4all-13b-snoozy](https://huggingface.co/nomic-ai/gpt4all-13b-snoozy)
- [NousResearch/Nous-Hermes-13b](https://huggingface.co/NousResearch/Nous-Hermes-13b)
- [openaccess-ai-collective/manticore-13b-chat-pyg](https://huggingface.co/openaccess-ai-collective/manticore-13b-chat-pyg)
- [OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5](https://huggingface.co/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5)
- [project-baize/baize-v2-7b](https://huggingface.co/project-baize/baize-v2-7b)
- [Salesforce/codet5p-6b](https://huggingface.co/Salesforce/codet5p-6b)
- [StabilityAI/stablelm-tuned-alpha-7b](https://huggingface.co/stabilityai/stablelm-tuned-alpha-7b)
- [THUDM/chatglm-6b](https://huggingface.co/THUDM/chatglm-6b)
- [THUDM/chatglm2-6b](https://huggingface.co/THUDM/chatglm2-6b)
- [tiiuae/falcon-40b](https://huggingface.co/tiiuae/falcon-40b)
- [timdettmers/guanaco-33b-merged](https://huggingface.co/timdettmers/guanaco-33b-merged)
- [togethercomputer/RedPajama-INCITE-7B-Chat](https://huggingface.co/togethercomputer/RedPajama-INCITE-7B-Chat)
- [WizardLM/WizardLM-13B-V1.0](https://huggingface.co/WizardLM/WizardLM-13B-V1.0)
- [WizardLM/WizardCoder-15B-V1.0](https://huggingface.co/WizardLM/WizardCoder-15B-V1.0)
- [baichuan-inc/baichuan-7B](https://huggingface.co/baichuan-inc/baichuan-7B)
- [internlm/internlm-chat-7b](https://huggingface.co/internlm/internlm-chat-7b)
- [Qwen/Qwen-7B-Chat/Qwen-14B-Chat](https://huggingface.co/Qwen/)
- [HuggingFaceH4/starchat-beta](https://huggingface.co/HuggingFaceH4/starchat-beta)
- [FlagAlpha/Llama2-Chinese-13b-Chat](https://huggingface.co/FlagAlpha/Llama2-Chinese-13b-Chat) and other models of FlagAlpha
- [BAAI/AquilaChat-7B](https://huggingface.co/BAAI/AquilaChat-7B)
- [all models of OpenOrca](https://huggingface.co/Open-Orca)
- [Spicyboros](https://huggingface.co/jondurbin/spicyboros-7b-2.2?not-for-all-audiences=true) + [airoboros 2.2](https://huggingface.co/jondurbin/airoboros-l2-13b-2.2)
- [baichuan2-7b/baichuan2-13b](https://huggingface.co/baichuan-inc)
- [VMware&#39;s OpenLLaMa OpenInstruct](https://huggingface.co/VMware/open-llama-7b-open-instruct)

* Any [EleutherAI](https://huggingface.co/EleutherAI) pythia model such as [pythia-6.9b](https://huggingface.co/EleutherAI/pythia-6.9b)(任何 [EleutherAI](https://huggingface.co/EleutherAI) 的 pythia 模型，如 [pythia-6.9b](https://huggingface.co/EleutherAI/pythia-6.9b))
* Any [Peft](https://github.com/huggingface/peft) adapter trained on top of a model above. To activate, must have `peft` in the model path. Note: If loading multiple peft models, you can have them share the base model weights by setting the environment variable `PEFT_SHARE_BASE_WEIGHTS=true` in any model worker.


The above model support list may be updated continuously as [FastChat](https://github.com/lm-sys/FastChat) is updated, see [FastChat Supported Models List](https://github.com/lm-sys/FastChat/blob/main /docs/model_support.md).
In addition to local models, this project also supports direct access to online models such as OpenAI API, Wisdom Spectrum AI, etc. For specific settings, please refer to the configuration information of `llm_model_dict` in `configs/model_configs.py.example`.
Online LLM models are currently supported:

- [ChatGPT](https://api.openai.com)
- [Smart Spectrum AI](http://open.bigmodel.cn)
- [MiniMax](https://api.minimax.chat)
- [Xunfei Starfire](https://xinghuo.xfyun.cn)
- [Baidu Qianfan](https://cloud.baidu.com/product/wenxinworkshop?track=dingbutonglan)
- [Aliyun Tongyi Qianqian](https://dashscope.aliyun.com/)

The default LLM type used in the project is `THUDM/chatglm2-6b`, if you need to use other LLM types, please modify `llm_model_dict` and `LLM_MODEL` in [configs/model_config.py].

### Supported Embedding models

Following models are tested by developers with Embedding class of [HuggingFace](https://huggingface.co/models?pipeline_tag=sentence-similarity):

- [moka-ai/m3e-small](https://huggingface.co/moka-ai/m3e-small)
- [moka-ai/m3e-base](https://huggingface.co/moka-ai/m3e-base)
- [moka-ai/m3e-large](https://huggingface.co/moka-ai/m3e-large)
- [BAAI/bge-small-zh](https://huggingface.co/BAAI/bge-small-zh)
- [BAAI/bge-base-zh](https://huggingface.co/BAAI/bge-base-zh)
- [BAAI/bge-large-zh](https://huggingface.co/BAAI/bge-large-zh)
- [BAAI/bge-large-zh-noinstruct](https://huggingface.co/BAAI/bge-large-zh-noinstruct)
- [sensenova/piccolo-base-zh](https://huggingface.co/sensenova/piccolo-base-zh)
- [sensenova/piccolo-large-zh](https://huggingface.co/sensenova/piccolo-large-zh)
- [shibing624/text2vec-base-chinese-sentence](https://huggingface.co/shibing624/text2vec-base-chinese-sentence)
- [shibing624/text2vec-base-chinese-paraphrase](https://huggingface.co/shibing624/text2vec-base-chinese-paraphrase)
- [shibing624/text2vec-base-multilingual](https://huggingface.co/shibing624/text2vec-base-multilingual)
- [shibing624/text2vec-base-chinese](https://huggingface.co/shibing624/text2vec-base-chinese)
- [shibing624/text2vec-bge-large-chinese](https://huggingface.co/shibing624/text2vec-bge-large-chinese)
- [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese)
- [nghuyong/ernie-3.0-nano-zh](https://huggingface.co/nghuyong/ernie-3.0-nano-zh)
- [nghuyong/ernie-3.0-base-zh](https://huggingface.co/nghuyong/ernie-3.0-base-zh)
- [sensenova/piccolo-base-zh](https://huggingface.co/sensenova/piccolo-base-zh)
- [sensenova/piccolo-base-zh](https://huggingface.co/sensenova/piccolo-large-zh)
- [OpenAI/text-embedding-ada-002](https://platform.openai.com/docs/guides/embeddings)

The default Embedding type used in the project is `sensenova/piccolo-base-zh`, if you want to use other Embedding types, please modify `embedding_model_dict` and `embedding_model_dict` and `embedding_model_dict` in [configs/model_config.py]. MODEL` in [configs/model_config.py].

### Build your own Agent tool!

See [Custom Agent Instructions](docs/自定义Agent.md) for details.

---

## Docker Deployment

🐳 Docker image path: `registry.cn-beijing.aliyuncs.com/chatchat/chatchat:0.2.5)`

```shell
docker run -d --gpus all -p 80:8501 registry.cn-beijing.aliyuncs.com/chatchat/chatchat:0.2.5
```

- The image size of this version is `33.9GB`, using `v0.2.0`, with `nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04` as the base image
- This version has a built-in `embedding` model: `m3e-large`, built-in `chatglm2-6b-32k`
- This version is designed to facilitate one-click deployment. Please make sure you have installed the NVIDIA driver on your Linux distribution.
- Please note that you do not need to install the CUDA toolkit on the host system, but you need to install the `NVIDIA Driver` and the `NVIDIA Container Toolkit`, please refer to the [Installation Guide](https://docs.nvidia.com/datacenter/cloud -native/container-toolkit/latest/install-guide.html)
- It takes a certain amount of time to pull and start for the first time. When starting for the first time, please refer to the figure below to use `docker logs -f <container id>` to view the log.
- If the startup process is stuck in the `Waiting..` step, it is recommended to use `docker exec -it <container id> bash` to enter the `/logs/` directory to view the corresponding stage logs

---

## Development

### Environment Prerequisite

The project is tested under Python3.8-python 3.10, CUDA 11.0-CUDA11.7, Windows, macOS of ARM architecture, and Linux platform.

### 1. Preparing Deployment Environment

Please refer to [install.md](docs/INSTALL.md)

### 2. Downloading model to local disk

**For offline deployment only!**

If you want to run this project in a local or offline environment, you need to first download the models required for the project to your local computer. Usually the open source LLM and Embedding models can be downloaded from [HuggingFace](https://huggingface.co/models).

Take the LLM model [THUDM/chatglm2-6b](https://huggingface.co/THUDM/chatglm2-6b) and Embedding model [moka-ai/m3e-base](https://huggingface. co/moka-ai/m3e-base) for example:

To download the model, you need to [install Git LFS](https://docs.github.com/zh/repositories/working-with-files/managing-large-files/installing-git-large-file-storage), and then run:

```Shell
$ git clone https://huggingface.co/THUDM/chatglm2-6b

$ git clone https://huggingface.co/moka-ai/m3e-base
```

### 3. Setting Configuration

Copy the model-related parameter configuration template file [configs/model_config.py.example](configs/model_config.py.example) and save it in the `./configs` path under the project path, and rename it to `model_config.py`.

Copy the service-related parameter configuration template file [configs/server_config.py.example](configs/server_config.py.example) to save in the `./configs` path under the project path, and rename it to `server_config.py`.

Before starting to execute Web UI or command line interaction, please check whether each model parameter in `configs/model_config.py` and `configs/server_config.py` meets the requirements.

* Please confirm that the path to local LLM model and embedding model have been written in `llm_dict` of `configs/model_config.py`, here is an example:
* If you choose to use OpenAI's Embedding model, please write the model's ``key`` into `embedding_model_dict`. To use this model, you need to be able to access the OpenAI official API, or set up a proxy.

```python
llm_model_dict={
                "chatglm2-6b": {
                        "local_model_path": "/Users/xxx/Downloads/chatglm2-6b",
                        "api_base_url": "http://localhost:8888/v1",  # "name"修改为 FastChat 服务中的"api_base_url"
                        "api_key": "EMPTY"
                    },
                }
```

```python
embedding_model_dict = {
                        "m3e-base": "/Users/xxx/Downloads/m3e-base",
                       }
```

### 4. Knowledge Base Migration

The knowledge base information  is stored in the database, please initialize the database before running the project (we strongly recommend one back up the knowledge files before performing operations).

- If you migrate from `0.1.x`, for the established knowledge base, please confirm that the vector library type and Embedding model of the knowledge base are consistent with the default settings in `configs/model_config.py`, if there is no change, simply add the existing repository information to the database with the following command:

  ```shell
  $ python init_database.py
  ```
- If you are a beginner of the project whose knowledge base has not been established, or the knowledge base type and embedding model in the configuration file have changed, or the previous vector library did not enable `normalize_L2`, you need the following command to initialize or rebuild the knowledge base:

  ```shell
  $ python init_database.py --recreate-vs
  ```

### 5. Launching API Service or WebUI with One Command

#### 5.1 Command

The script is `startuppy`, you can luanch all fastchat related, API,WebUI service with is, here is an example:

```shell
$ python startup.py -a
```

optional args including: `-a(or --all-webui), --all-api, --llm-api, -c(or --controller),--openai-api, -m(or --model-worker), --api, --webui`, where:

* `--all-webui` means to launch all related services of WEBUI
* `--all-api` means to launch all related services of API
* `--llm-api` means to launch all related services of FastChat
* `--openai-api` means to launch controller and openai-api-server  of FastChat only
* `model-worker` means to launch model worker of FastChat only
* any other optional arg is to launch one particular function only

#### 5.2 Launch none-default model

If you want to specify a none-default model, use `--model-name` arg, here is a example:

```shell
$ python startup.py --all-webui --model-name Qwen-7B-Chat
```

#### 5.3 Load model with multi-gpus

If you want to load model with multi-gpus, then the following three parameters in `startup.create_model_worker_app` should be changed:

```python
gpus=None, 
num_gpus=1, 
max_gpu_memory="20GiB"
```

where:

* `gpus` is about specifying the gpus' ID, such as '0,1';
* `num_gpus` is about specifying the number of gpus to be used under `gpus`;
* `max_gpu_memory` is about specifying the gpu memory of every gpu.

note:

* These parameters now can be specified by `server_config.FSCHST_MODEL_WORKERD`.
* In some extreme senses, `gpus` doesn't work, then one should specify the used gpus with environment variable `CUDA_VISIBLE_DEVICES`, here is an example:

```shell
CUDA_VISIBLE_DEVICES=0,1 python startup.py -a
```

#### 5.4 Load PEFT

Including lora,p-tuning,prefix tuning, prompt tuning,ia3

This project loads the LLM service based on FastChat, so one must load the PEFT in a FastChat way, that is, ensure that the word `peft` must be in the path name, the name of the configuration file must be `adapter_config.json`, and the path contains PEFT weights in `.bin` format. The peft path is specified in `args.model_names` of the `create_model_worker_app` function in `startup.py`, and enable the environment variable `PEFT_SHARE_BASE_WEIGHTS=true` parameter.

If the above method fails, you need to start standard fastchat service step by step.  Step-by-step procedure could be found Section 6. For further steps, please refer to [Model invalid after loading lora fine-tuning](https://github. com/chatchat-space/Langchain-Chatchat/issues/1130#issuecomment-1685291822).

#### **5.5 Some Notes**

1. **The `startup.py` uses multi-process mode to start the services of each module, which may cause printing order problems. Please wait for all services to be initiated before calling, and call the service according to the default or specified port (default LLM API service port: `127.0.0.1:8888 `, default API service port:`127.0.0.1:7861 `, default WebUI service port: `127.0.0.1: 8501`)**
2. **The startup time of the service differs across devices, usually it takes 3-10 minutes. If it does not start for a long time, please go to the `./logs` directory to monitor the logs and locate the problem.**
3. **Using ctrl+C to exit on Linux may cause orphan processes due to the multi-process mechanism of Linux. You can exit through `shutdown_all.sh`**

#### 5.6 Interface Examples

The API, chat interface of WebUI, and knowledge management interface of WebUI are list below respectively.

1. FastAPI docs

![](img/fastapi_docs_020_0.png)

2. Chat Interface of WebUI

- Dialogue interface of WebUI

![img](img/webui_0915_0.png)

- Knowledge management interface of WebUI

![img](img/webui_0915_1.png)

## FAQ

Please refer to [FAQ](docs/FAQ.md)

---

## Roadmap

- [X] Langchain applications

  - [X] Load local documents
    - [X] Unstructured documents
      - [X] .md
      - [X] .txt
      - [X] .docx
    - [ ] Structured documents
      - [X] .csv
      - [ ] .xlsx
    - [] TextSplitter and Retriever
      - [X] multiple TextSplitter
      - [X] ChineseTextSplitter
      - [ ] Reconstructed Context Retriever
    - [ ] Webpage
    - [ ] SQL
    - [ ] Knowledge Database
  - [X] Search Engines
    - [X] Bing
    - [X] DuckDuckGo
  - [X] Agent
    - [X] Agent implementation in the form of basic React, including calls to calculators, etc.
    - [X] Langchain's own Agent implementation and calls
    - [ ] More Agent support for models
    - [ ] More tools
- [X] LLM  Models
  - [X] [FastChat](https://github.com/lm-sys/fastchat) -based LLM Models
  - [ ] Mutiply Remote LLM API
- [X] Embedding Models
  - [X] HuggingFace -based Embedding models
  - [ ] Mutiply Remote Embedding API
- [X] FastAPI-based API
- [X] Web UI
  - [X] Streamlit -based Web UI

---

## Wechat Group

<img src="img/qr_code_64.jpg" alt="QR Code" width="300" height="300" />

🎉 langchain-Chatchat project WeChat exchange group, if you are also interested in this project, welcome to join the group chat to participate in the discussion and exchange.

## Follow us

<img src="img/official_account.png" alt="image" width="900" height="300" />
🎉 langchain-Chatchat project official public number, welcome to scan the code to follow.
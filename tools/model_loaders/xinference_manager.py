import json
import os

import pandas as pd
import streamlit as st
from xinference.client import Client
import xinference.model.llm as xf_llm
from xinference.model import embedding as xf_embedding
from xinference.model import image as xf_image
from xinference.model import rerank as xf_rerank
from xinference.model import audio as xf_audio
from xinference.constants import XINFERENCE_CACHE_DIR


model_types = ["LLM", "embedding", "image", "rerank", "audio"]
model_name_suffix = "-custom"
cache_methods = {
    "LLM": xf_llm.llm_family.cache,
    "embedding": xf_embedding.core.cache,
    "image": xf_image.core.cache,
    "rerank": xf_rerank.core.cache,
    "audio": xf_audio.core.cache,
}


@st.cache_resource
def get_client(url: str):
    return Client(url)


def get_cache_dir(
    model_type: str,
    model_name: str,
    model_format: str = "",
    model_size: str = "",
):
    if model_type == "LLM":
        dir_name = f"{model_name}-{model_format}-{model_size}b"
    else:
        dir_name = f"{model_name}"
    return os.path.join(XINFERENCE_CACHE_DIR, dir_name)


def get_meta_path(
    model_type: str,
    cache_dir: str,
    model_format: str,
    model_hub: str = "huggingface",
    model_quant: str = "none",
):
    if model_type == "LLM":
        return xf_llm.llm_family._get_meta_path(
            cache_dir=cache_dir,
            model_format=model_format,
            model_hub=model_hub,
            quantization=model_quant,
        )
    else:
        return os.path.join(cache_dir, "__valid_download")


def list_running_models():
    models = client.list_models()
    columns = [
        "UID",
        "type",
        "name",
        "ability",
        "size",
        "quant",
        "max_tokens",
    ]
    data = []
    for k, v in models.items():
        item = dict(
                UID=k,
                type=v["model_type"],
                name=v["model_name"],
        )
        if v["model_type"] == "LLM":
            item.update(
                ability=v["model_ability"],
                size=str(v["model_size_in_billions"]) + "B",
                quant=v["quantization"],
                max_tokens=v["context_length"],
            )
        elif v["model_type"] == "embedding":
            item.update(
                max_tokens=v["max_tokens"],
            )
        data.append(item)
    df = pd.DataFrame(data, columns=columns)
    df.index += 1
    return df


def get_model_registrations():
    data = {}
    for model_type in model_types:
        data[model_type] = {}
        for m in client.list_model_registrations(model_type):
            data[model_type][m["model_name"]] = {"is_builtin": m["is_builtin"]}
            reg = client.get_model_registration(model_type, m["model_name"])
            data[model_type][m["model_name"]]["reg"] = reg
    return data


with st.sidebar:
    st.subheader("请先执行 xinference 或 xinference-local 命令启动 XF 服务。然后将 XF 服务地址配置在下方。")
    xf_url = st.text_input("Xinference endpoint", "http://127.0.0.1:9997")
    st.divider()
    st.markdown(
        "### 使用方法\n\n"
        "- 场景1：我已经下载过模型，不想 XF 内置模型重复下载\n\n"
        "- 操作：选择对应的模型后，填写好本地模型路径，点‘设置模型缓存’即可\n\n"
        "- 场景2：我想对 XF 内置模型做一些修改，又不想从头写模型注册文件\n\n"
        "- 操作：选择对应的模型后，填写好本地模型路径，点‘注册为自定义模型’即可\n\n"
        "- 场景3：我不小心设置了错误的模型路径\n\n"
        "- 操作：直接‘删除模型缓存’或更换正确的路径后‘设置模型缓存’即可\n\n"
    )
client = get_client(xf_url)


st.subheader("当前运行的模型：")
st.dataframe(list_running_models())

st.subheader("配置模型路径：")
regs = get_model_registrations()
cols = st.columns([3, 4, 3, 2, 2])

model_type = cols[0].selectbox("模型类别：", model_types)

model_names = list(regs[model_type].keys())
model_name = cols[1].selectbox("模型名称：", model_names)

cur_reg = regs[model_type][model_name]["reg"]
model_format = None
model_quant = None

if model_type == "LLM":
    cur_family = xf_llm.LLMFamilyV1.parse_obj(cur_reg)
    cur_spec = None
    model_formats = []
    for spec in cur_reg["model_specs"]:
        if spec["model_format"] not in model_formats:
            model_formats.append(spec["model_format"])
    index = 0
    if "pytorch" in model_formats:
        index = model_formats.index("pytorch")
    model_format = cols[2].selectbox("模型格式：", model_formats, index)

    model_sizes = []
    for spec in cur_reg["model_specs"]:
        if (spec["model_format"] == model_format
            and spec["model_size_in_billions"] not in model_sizes):
            model_sizes.append(spec["model_size_in_billions"])
    model_size = cols[3].selectbox("模型大小：", model_sizes, format_func=lambda x: f"{x}B")

    model_quants = []
    for spec in cur_reg["model_specs"]:
        if (spec["model_format"] == model_format
            and spec["model_size_in_billions"] == model_size):
            model_quants = spec["quantizations"]
    model_quant = cols[4].selectbox("模型量化：", model_quants)
    if model_quant == "none":
        model_quant = None

    for i, spec in enumerate(cur_reg["model_specs"]):
        if (spec["model_format"] == model_format
            and spec["model_size_in_billions"] == model_size):
            cur_spec = cur_family.model_specs[i]
            break
    cache_dir = get_cache_dir(model_type, model_name, model_format, model_size)
elif model_type == "embedding":
    cur_spec = xf_embedding.core.EmbeddingModelSpec.parse_obj(cur_reg)
    cache_dir = get_cache_dir(model_type, model_name)
elif model_type == "image":
    cur_spec = xf_image.core.ImageModelFamilyV1.parse_obj(cur_reg)
    cache_dir = get_cache_dir(model_type, model_name)
elif model_type == "rerank":
    cur_spec = xf_rerank.core.RerankModelSpec.parse_obj(cur_reg)
    cache_dir = get_cache_dir(model_type, model_name)
elif model_type == "audio":
    cur_spec = xf_audio.core.AudioModelFamilyV1.parse_obj(cur_reg)
    cache_dir = get_cache_dir(model_type, model_name)

meta_file = get_meta_path(
    model_type=model_type,
    model_format=model_format,
    cache_dir=cache_dir,
    model_quant=model_quant)

if os.path.isdir(cache_dir):
    try:
        with open(meta_file, encoding="utf-8") as fp:
            meta = json.load(fp)
        revision = meta.get("revision", meta.get("model_revision"))
    except:
        revision = None

    if revision is None:
        revision = "None"

    if cur_spec.model_revision and cur_spec.model_revision != revision:
        revision += " (与 XF 内置版本号不一致)"
    else:
        revision += " (符合要求)"

    text = (f"模型已缓存。\n\n"
            f"缓存路径：{cache_dir}\n\n"
            f"原始路径：{os.readlink(cache_dir)[4:]}\n\n"
            f"版本号  ：{revision}"
    )
else:
    text = "模型尚未缓存"

st.divider()
st.markdown(text)
st.divider()

local_path = st.text_input("本地模型绝对路径：")
cols = st.columns(3)

if cols[0].button("设置模型缓存"):
    if os.path.isabs(local_path) and os.path.isdir(local_path):
        cur_spec.__dict__["model_uri"] = local_path # embedding spec has no attribute model_uri
        if os.path.isdir(cache_dir):
            os.rmdir(cache_dir)
        if model_type == "LLM":
            cache_methods[model_type](cur_family, cur_spec, model_quant)
            xf_llm.llm_family._generate_meta_file(meta_file, cur_family, cur_spec, model_quant)
        else:
            cache_methods[model_type](cur_spec)
        if cur_spec.model_revision:
            for hub in ["huggingface", "modelscope"]:
                meta_file = get_meta_path(
                    model_type=model_type,
                    model_format=model_format,
                    model_hub=hub,
                    cache_dir=cache_dir,
                    model_quant=model_quant)
            with open(meta_file, "w", encoding="utf-8") as fp:
                json.dump({"revision": cur_spec.model_revision}, fp)
        st.rerun()
    else:
        st.error("必须输入存在的绝对路径")

if cols[1].button("删除模型缓存"):
    if os.path.isdir(cache_dir):
        os.rmdir(cache_dir)

if cols[2].button("注册为自定义模型"):
    if os.path.isabs(local_path) and os.path.isdir(local_path):
        cur_spec.model_uri = local_path
        cur_spec.model_revision = None
        if model_type == "LLM":
            cur_family.model_name = f"{cur_family.model_name}{model_name_suffix}"
            cur_family.model_family = "other"
            model_definition = cur_family.model_dump_json(indent=2, ensure_ascii=False)
        else:
            cur_spec.model_name = f"{cur_spec.model_name}{model_name_suffix}"
            model_definition = cur_spec.model_dump_json(indent=2, ensure_ascii=False)
        client.register_model(
            model_type=model_type,
            model=model_definition,
            persist=True,
        )
        st.rerun()
    else:
        st.error("必须输入存在的绝对路径")

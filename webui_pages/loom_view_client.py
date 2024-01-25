from typing import Tuple, Any

import streamlit as st
from loom_core.openai_plugins.publish import LoomOpenAIPluginsClient
import logging

logger = logging.getLogger(__name__)
client = LoomOpenAIPluginsClient(base_url="http://localhost:8000", timeout=300, use_async=False)


def update_store():
    logger.info("update_status")
    st.session_state.status = client.status()
    logger.info("update_list_plugins")
    list_plugins = client.list_plugins()
    st.session_state.run_plugins_list = list_plugins.get("plugins_list", [])

    logger.info("update_launch_subscribe_info")
    launch_subscribe_info = {}
    for plugin_name in st.session_state.run_plugins_list:
        launch_subscribe_info[plugin_name] = client.launch_subscribe_info(plugin_name)

    st.session_state.launch_subscribe_info = launch_subscribe_info

    logger.info("update_list_running_models")
    list_running_models = {}
    for plugin_name in st.session_state.run_plugins_list:
        list_running_models[plugin_name] = client.list_running_models(plugin_name)
    st.session_state.list_running_models = list_running_models

    logger.info("update_model_config")
    model_config = {}
    for plugin_name in st.session_state.run_plugins_list:
        model_config[plugin_name] = client.list_llm_models(plugin_name)
    st.session_state.model_config = model_config


def start_plugin():
    import time
    start_plugins_name = st.session_state.plugins_name
    if start_plugins_name in st.session_state.run_plugins_list:
        st.toast(start_plugins_name + " has already been counted.")

        time.sleep(.5)
    else:

        st.toast("start_plugin " + start_plugins_name + ",starting.")
        result = client.launch_subscribe(start_plugins_name)
        st.toast("start_plugin " + start_plugins_name + " ." + result.get("detail", ""))
        time.sleep(3)
        result1 = client.launch_subscribe_start(start_plugins_name)

        st.toast("start_plugin " + start_plugins_name + " ." + result1.get("detail", ""))
        time.sleep(2)
        update_store()


def start_worker():
    select_plugins_name = st.session_state.plugins_name
    select_worker_id = st.session_state.worker_id
    start_model_list = st.session_state.list_running_models.get(select_plugins_name, [])
    already_counted = False
    for model in start_model_list:
        if model['worker_id'] == select_worker_id:
            already_counted = True
            break

    if already_counted:
        st.toast(
            "select_plugins_name " + select_plugins_name + ",worker_id " + select_worker_id + " has already been counted.")
        import time
        time.sleep(.5)
    else:

        st.toast("select_plugins_name " + select_plugins_name + ",worker_id " + select_worker_id + " starting.")
        result = client.launch_subscribe_start_model(select_plugins_name, select_worker_id)
        st.toast("start worker_id " + select_worker_id + " ." + result.get("detail", ""))
        import time
        time.sleep(.5)
        update_store()


def stop_worker():
    select_plugins_name = st.session_state.plugins_name
    select_worker_id = st.session_state.worker_id
    start_model_list = st.session_state.list_running_models.get(select_plugins_name, [])
    already_counted = False
    for model in start_model_list:
        if model['worker_id'] == select_worker_id:
            already_counted = True
            break

    if not already_counted:
        st.toast("select_plugins_name " + select_plugins_name + ",worker_id " + select_worker_id + " has bad already")
        import time
        time.sleep(.5)
    else:

        st.toast("select_plugins_name " + select_plugins_name + ",worker_id " + select_worker_id + " stopping.")
        result = client.launch_subscribe_stop_model(select_plugins_name, select_worker_id)
        st.toast("stop worker_id " + select_worker_id + " ." + result.get("detail", ""))
        import time
        time.sleep(.5)
        update_store()


def build_providers_model_plugins_name():
    import streamlit_antd_components as sac
    if "run_plugins_list" not in st.session_state:
        return []
    # 按照模型构建sac.menu(菜单
    menu_items = []
    for key, value in st.session_state.list_running_models.items():
        menu_item_children = []
        for model in value:
            if "model" in model["providers"]:
                menu_item_children.append(sac.MenuItem(model["model_name"], description=model["model_description"]))

        menu_items.append(sac.MenuItem(key, icon='box-fill', children=menu_item_children))

    return menu_items


def build_providers_embedding_plugins_name():
    import streamlit_antd_components as sac
    if "run_plugins_list" not in st.session_state:
        return []
    # 按照模型构建sac.menu(菜单
    menu_items = []
    for key, value in st.session_state.list_running_models.items():
        menu_item_children = []
        for model in value:
            if "embedding" in model["providers"]:
                menu_item_children.append(sac.MenuItem(model["model_name"], description=model["model_description"]))

        menu_items.append(sac.MenuItem(key, icon='box-fill', children=menu_item_children))

    return menu_items


def find_menu_items_by_index(menu_items, key):
    for menu_item in menu_items:
        if menu_item.get('children') is not None:
            for child in menu_item.get('children'):
                if child.get('key') == key:
                    return menu_item, child

    return None, None


def set_llm_select(plugins_info, llm_model_worker):
    st.session_state["select_plugins_info"] = plugins_info
    st.session_state["select_model_worker"] = llm_model_worker


def get_select_model_endpoint() -> Tuple[str, str]:
    plugins_info = st.session_state["select_plugins_info"]
    llm_model_worker = st.session_state["select_model_worker"]
    if plugins_info is None or llm_model_worker is None:
        raise ValueError("plugins_info or llm_model_worker is None")
    plugins_name = st.session_state["select_plugins_info"]['label']
    select_model_name = st.session_state["select_model_worker"]['label']
    adapter_description = st.session_state.launch_subscribe_info[plugins_name]
    endpoint_host = adapter_description.get("adapter_description", {}).get("endpoint_host", "")
    return endpoint_host, select_model_name


def set_embed_select(plugins_info, embed_model_worker):
    st.session_state["select_embed_plugins_info"] = plugins_info
    st.session_state["select_embed_model_worker"] = embed_model_worker


def get_select_embed_endpoint() -> Tuple[str, str]:
    select_embed_plugins_info = st.session_state["select_embed_plugins_info"]
    select_embed_model_worker = st.session_state["select_embed_model_worker"]
    if select_embed_plugins_info is None or select_embed_model_worker is None:
        raise ValueError("select_embed_plugins_info or select_embed_model_worker is None")
    embed_plugins_name = st.session_state["select_embed_plugins_info"]['label']
    select_embed_model_name = st.session_state["select_embed_model_worker"]['label']
    endpoint_host = None
    if embed_plugins_name in st.session_state.launch_subscribe_info:
        adapter_description = st.session_state.launch_subscribe_info[embed_plugins_name]
        endpoint_host = adapter_description.get("adapter_description", {}).get("endpoint_host", "")
    return endpoint_host, select_embed_model_name

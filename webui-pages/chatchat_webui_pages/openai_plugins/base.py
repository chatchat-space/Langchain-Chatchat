import streamlit as st
from loom_openai_plugins_frontend import loom_openai_plugins_frontend

from chatchat_webui_pages.utils import ApiRequest
from chatchat_webui_pages.loom_view_client import (
    update_store,
    start_plugin,
    start_worker,
    stop_worker,
)


def openai_plugins_page(api: ApiRequest, is_lite: bool = None):


    with (st.container()):

        if "worker_id" not in st.session_state:
            st.session_state.worker_id = ''
        if "plugins_name" not in st.session_state and "status" in st.session_state:

            for k, v in st.session_state.status.get("status", {}).get("subscribe_status", []).items():
                st.session_state.plugins_name = v.get("plugins_names", [])[0]
                break

        col1, col2 = st.columns([0.8, 0.2])

        with col1:
            event = loom_openai_plugins_frontend(plugins_status=st.session_state.status,
                                                 run_list_plugins=st.session_state.run_plugins_list,
                                                 launch_subscribe_info=st.session_state.launch_subscribe_info,
                                                 list_running_models=st.session_state.list_running_models,
                                                 model_config=st.session_state.model_config)

        with col2:
            st.write("操作")
            if not st.session_state.run_plugins_list:
                button_type_disabled = False
                button_start_text = '启动'
            else:
                button_type_disabled = True
                button_start_text = '已启动'

            if event:
                event_type = event.get("event")
                if event_type == "BottomNavigationAction":
                    st.session_state.plugins_name = event.get("data")
                    st.session_state.worker_id = ''
                    # 不存在run_plugins_list，打开启动按钮
                    if st.session_state.plugins_name not in st.session_state.run_plugins_list \
                            or st.session_state.run_plugins_list:
                        button_type_disabled = False
                        button_start_text = '启动'
                    else:
                        button_type_disabled = True
                        button_start_text = '已启动'
                if event_type == "CardCoverComponent":
                    st.session_state.worker_id = event.get("data")

            st.button(button_start_text, disabled=button_type_disabled, key="start",
                      on_click=start_plugin)

            if st.session_state.worker_id != '':
                st.button("启动" + st.session_state.worker_id, key="start_worker",
                          on_click=start_worker)
                st.button("停止" + st.session_state.worker_id, key="stop_worker",
                          on_click=stop_worker)

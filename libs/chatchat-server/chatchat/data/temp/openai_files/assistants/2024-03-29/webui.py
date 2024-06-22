import os
import sys

import streamlit as st
from streamlit_option_menu import option_menu

from chatchat.configs import VERSION
from chatchat.server.utils import api_address
from chatchat.webui_pages.dialogue.dialogue import chat_box, dialogue_page
from chatchat.webui_pages.knowledge_base.knowledge_base import knowledge_base_page

# from chatchat.webui_pages.loom_view_client import update_store
# from chatchat.webui_pages.openai_plugins import openai_plugins_page
from chatchat.webui_pages.utils import *

# def on_change(key):
#     if key:
#         update_store()
img_dir = os.path.dirname(os.path.abspath(__file__))

api = ApiRequest(base_url=api_address())

if __name__ == "__main__":
    is_lite = "lite" in sys.argv

    st.set_page_config(
        "Langchain-Chatchat WebUI",
        os.path.join(img_dir, "img", "chatchat_icon_blue_square_v2.png"),
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/chatchat-space/Langchain-Chatchat",
            "Report a bug": "https://github.com/chatchat-space/Langchain-Chatchat/issues",
            "About": f"""欢迎使用 Langchain-Chatchat WebUI {VERSION}！""",
        },
        layout="wide",
    )

    # use the following code to set the app to wide mode and the html markdown to increase the sidebar width
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
            width: 350px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
            width: 600px;
            margin-left: -600px;
        }
         
        """,
        unsafe_allow_html=True,
    )
    pages = {
        "对话": {
            "icon": "chat",
            "func": dialogue_page,
        },
        "知识库管理": {
            "icon": "hdd-stack",
            "func": knowledge_base_page,
        },
        # "模型服务": {
        #     "icon": "hdd-stack",
        #     "func": openai_plugins_page,
        # },
    }
    # 更新状态
    # if "status" not in st.session_state \
    #         or "run_plugins_list" not in st.session_state \
    #         or "launch_subscribe_info" not in st.session_state \
    #         or "list_running_models" not in st.session_state \
    #         or "model_config" not in st.session_state:
    #     update_store()
    with st.sidebar:
        st.image(
            os.path.join(img_dir, "img", "logo-long-chatchat-trans-v2.png"),
            use_column_width=True,
        )
        st.caption(
            f"""<p align="right">当前版本：{VERSION}</p>""",
            unsafe_allow_html=True,
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            menu_title="",
            key="selected_page",
            options=options,
            icons=icons,
            # menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"](api=api, is_lite=is_lite)

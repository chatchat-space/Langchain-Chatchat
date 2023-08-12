# 运行方式：
# 1. 安装必要的包：pip install streamlit-option-menu streamlit-chatbox>=1.1.6
# 2. 运行本机fastchat服务：python server\llm_api.py 或者 运行对应的sh文件
# 3. 运行API服务器：python server/api.py。如果使用api = ApiRequest(no_remote_api=True)，该步可以跳过。
# 4. 运行WEB UI：streamlit run webui.py --server.port 7860

import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages import *

api = ApiRequest(base_url="http://127.0.0.1:7861", no_remote_api=False)

if __name__ == "__main__":
    st.set_page_config("langchain-chatglm WebUI")

    if not chat_box.chat_inited:
        st.toast(
            f"欢迎使用 [`Langchain-Chatglm`](https://github.com/chatchat-space/langchain-chatglm) ! \n\n"
            f"当前使用模型`{LLM_MODEL}`, 您可以开始提问了."
        )

    if "chat_list" not in st.session_state:
        st.session_state["chat_list"] = {"对话1": {"need_rename": True}}
    if "cur_chat_name" not in st.session_state:
        st.session_state["cur_chat_name"] = list(st.session_state["chat_list"].keys())[0]
    if "need_chat_name" not in st.session_state:
        st.session_state["need_chat_name"] = True

    pages = {i: {
        "icon": "chat",
        "func": dialogue_page,
    } for i in st.session_state.chat_list.keys()}

    pages2 = {
        "新建对话": {
            "icon": "plus-circle",
            "func": dialogue_page,
        },
        "---": {
            "icon": None,
            "func": None
        },
        "知识库管理": {
            "icon": "hdd-stack",
            "func": knowledge_base_page,
        },
    }
    pages.update(pages2)


    def on_change(key):
        selection = st.session_state[key]
        st.write(f"Selection changed to {selection}")

    def on_page_change(key):
        cur_chat_name = st.session_state["cur_chat_name"]
        if (st.session_state[key] == "新建对话"
            and not st.session_state.chat_list[cur_chat_name].get("need_rename")):
            new_chat_name = f"对话{len(st.session_state.chat_list) + 1}"
            st.session_state.chat_list[new_chat_name] = {"need_rename": True}
            st.session_state["cur_chat_name"] = new_chat_name
            st.session_state[key]  = new_chat_name

    with st.sidebar:
        selected_page = option_menu(
            "langchain-chatglm",
            options=list(pages.keys()),
            icons=[i["icon"] for i in pages.values()],
            menu_icon="chat-quote",
            key="selected_page",
            on_change=on_page_change,
        )

    pages[selected_page]["func"](api)

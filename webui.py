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
    st.set_page_config("langchain-chatglm WebUI", initial_sidebar_state="expanded")

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

    chat_list = [{"name": k, "chat_no": v.get("chat_no", 0)} for k, v in st.session_state.chat_list.items()]
    pages = {i["name"]: {
        "icon": "chat",
        "func": dialogue_page,
    } for i in sorted(chat_list, key=lambda x: x["chat_no"])}

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
        
    with st.sidebar:
        default_index = list(pages).index(st.session_state["cur_chat_name"])
        selected_page = option_menu(
            "langchain-chatglm",
            options=list(pages.keys()),
            icons=[i["icon"] for i in pages.values()],
            menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page == "新建对话":
        cur_chat_name = st.session_state["cur_chat_name"]
        if (not st.session_state.get("create_chat")
            and not st.session_state.get("renamde_chat")
            and not st.session_state.get("delete_chat")):
            chat_no = len(st.session_state.chat_list) + 1
            new_chat_name = f"对话{chat_no}"
            st.session_state.chat_list[new_chat_name] = {"need_rename": True, "chat_no": chat_no}
            st.session_state["cur_chat_name"] = new_chat_name
            st.experimental_rerun()
        if st.session_state.get("create_chat"):
            st.session_state.create_chat = False
        if st.session_state.get("renamde_chat"):
            st.session_state.renamde_chat = False
        if st.session_state.get("delete_chat"):
            st.session_state.delete_chat = False
    elif selected_page in st.session_state.chat_list:
        st.session_state["cur_chat_name"] = selected_page

    if selected_page in pages:
        pages[selected_page]["func"](api)

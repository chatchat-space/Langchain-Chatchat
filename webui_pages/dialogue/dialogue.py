import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *
from datetime import datetime
import streamlit_antd_components as sac
from server.chat.search_engine_chat import SEARCH_ENGINES
from typing import List, Dict


chat_box = ChatBox()

def get_messages_history(history_len: int) -> List[Dict]:
    def filter(msg):
        '''
        针对当前简单文本对话，只返回每条消息的第一个element的内容
        '''
        content = [x._content for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        return {
            "role": msg["role"],
            "content": content[0] if content else "",
        }
    history = chat_box.filter_history(100000, filter) # workaround before upgrading streamlit-chatbox.
    user_count = 0
    i = 1
    for i in range(1, len(history) + 1):
        if history[-i]["role"] == "user":
            user_count += 1
            if user_count >= history_len:
                break
    return history[-i:]


def dialogue_page(api: ApiRequest):
    chat_box.init_session()

    with st.sidebar:
        with st.expander("会话管理", True):
            col_input, col_btn = st.columns(2)
            new_chat_name = col_input.text_input(
                "新会话名称",
                placeholder="新会话名称",
                label_visibility="collapsed",
                key="new_chat_name",
            )

            def on_btn_new_chat():
                new_chat_name = st.session_state.new_chat_name
                if new_chat_name:
                    chat_box.use_chat_name(new_chat_name)
                    st.session_state.new_chat_name = ""
            col_btn.button("新建会话", on_click=on_btn_new_chat)

            chat_list = chat_box.get_chat_names()
            cur_chat_name = sac.buttons(chat_list, 0)
            chat_box.use_chat_name(cur_chat_name)

            cols = st.columns(3)
            export_btn = cols[0]
            if cols[1].button("Clear"):
                chat_box.reset_history()

            if cols[2].button("Delete"):
                chat_box.del_chat_name(cur_chat_name, disabled=len(chat_list) <= 1)

        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"已切换到 {mode} 模式。"
            if mode == "知识库问答":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} 当前知识库： `{cur_kb}`。"
            st.toast(text)
            # sac.alert(text, description="descp", type="success", closable=True, banner=True)

        dialogue_mode = st.radio("请选择对话模式",
                                 ["LLM 对话",
                                  "知识库问答",
                                  "搜索引擎问答",
                                ],
                                on_change=on_mode_change,
                                key="dialogue_mode",
                                )
        history_len = st.slider("历史对话轮数：", 1, 10, 3)
        # todo: support history len

        def on_kb_change():
            st.toast(f"已加载知识库： {st.session_state.selected_kb}")

        if dialogue_mode == "知识库问答":
            with st.expander("知识库配置", True):
                kb_list = api.list_knowledge_bases(no_remote_api=True)
                selected_kb = st.selectbox(
                    "请选择知识库：",
                    kb_list,
                    on_change=on_kb_change,
                    key="selected_kb",
                )
                kb_top_k = st.slider("匹配知识条数：", 1, 20, 3)
                score_threshold = st.slider("知识匹配分数阈值：", 0, 1000, 0, disabled=True)
                chunk_content = st.checkbox("关联上下文", False, disabled=True)
                chunk_size = st.slider("关联长度：", 0, 500, 250, disabled=True)
        elif dialogue_mode == "搜索引擎问答":
            search_engine = sac.buttons(SEARCH_ENGINES.keys(), 0)
            se_top_k = st.slider("匹配搜索结果条数：", 1, 20, 3)

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    if prompt := st.chat_input("请输入对话内容，换行请使用Ctrl+Enter"):
        history = get_messages_history(history_len)
        chat_box.user_say(prompt)
        if dialogue_mode == "LLM 对话":
            chat_box.ai_say("正在思考...")
            text = ""
            r = api.chat_chat(prompt, history)
            for t in r:
                text += t
                chat_box.update_msg(text)
            chat_box.update_msg(text, streaming=False) # 更新最终的字符串，去除光标
        elif dialogue_mode == "知识库问答":
            history = get_messages_history(history_len)
            chat_box.ai_say([
                f"正在查询知识库： `{selected_kb}` ...",
                Markdown("...", in_expander=True, title="知识库匹配结果"),
            ])
            text = ""
            for d in api.knowledge_base_chat(prompt, selected_kb, kb_top_k, history):
                text += d["answer"]
                chat_box.update_msg(text, 0)
                chat_box.update_msg("\n\n".join(d["docs"]), 1, streaming=False)
            chat_box.update_msg(text, 0, streaming=False)
        elif dialogue_mode == "搜索引擎问答":
            chat_box.ai_say([
                f"正在执行{search_engine}搜索...",
                Markdown("...", in_expander=True, title="网络搜索结果"),
            ])
            text = ""
            for d in api.bing_search_chat(prompt, search_engine, se_top_k):
                text += d["answer"]
                chat_box.update_msg(text, 0)
                chat_box.update_msg("\n\n".join(d["docs"]), 1, streaming=False)
            chat_box.update_msg(text, 0, streaming=False)

    now = datetime.now()
    export_btn.download_button(
        "Export",
        "".join(chat_box.export2md(cur_chat_name)),
        file_name=f"{now:%Y-%m-%d %H.%M}_{cur_chat_name}.md",
        mime="text/markdown",
    )

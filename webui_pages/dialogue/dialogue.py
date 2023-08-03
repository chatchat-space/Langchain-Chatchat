import streamlit as st
from webui_pages.utils import *
from streamlit_chatbox import *


def dialogue_page(api: ApiRequest):
    chat_box = ChatBox(
        greetings=[
            f"欢迎使用 [`Langchain-Chatglm`](https://github.com/chatchat-space/langchain-chatglm) ! 当前使用模型`{LLM_MODEL}`, 您可以开始提问了.",
        ]
    )

    with st.sidebar:
        def on_mode_change():
            mode = st.session_state.dialogue_mode
            text = f"已切换到 {mode} 模式。"
            if mode == "知识库问答":
                cur_kb = st.session_state.get("selected_kb")
                if cur_kb:
                    text = f"{text} 当前知识库： `{cur_kb}`。"
            chat_box.ai_say(text, not_render=True)

        dialogue_mode = st.radio("请选择对话模式",
                                 ["LLM 对话",
                                  "知识库问答",
                                  "Bing 搜索问答",
                                  "Duck 搜索问答",
                                ],
                                on_change=on_mode_change,
                                key="dialogue_mode",
                                )
        history_len = st.slider("历史对话轮数：", 1, 10, 1, disabled=True)
        # todo: support history len
        if st.button("清除历史对话"):
            chat_box.reset_history()

        def on_kb_change():
            chat_box.ai_say(f"已加载知识库： {st.session_state.selected_kb}", not_render=True)

        if dialogue_mode == "知识库问答":
            kb_list = api.list_knowledge_bases()
            selected_kb = st.selectbox(
                "请选择知识库：",
                kb_list,
                on_change=on_kb_change,
                key="selected_kb",
            )
            top_k = st.slider("匹配知识条数：", 1, 20, 3, disabled=True)
            score_threshold = st.slider("知识匹配分数阈值：", 0, 1000, 0, disabled=True)
            chunk_content = st.checkbox("关联上下文", False, disabled=True)
            chunk_size = st.slider("关联长度：", 0, 500, 250, disabled=True)

    # Display chat messages from history on app rerun
    chat_box.output_messages()

    if prompt := st.chat_input("请输入对话内容，换行请使用Ctrl+Enter"):
        chat_box.user_say(prompt)
        if dialogue_mode == "LLM 对话":
            chat_box.ai_say("正在思考...")
            text = ""
            r = api.chat_chat(prompt, no_remote_api=True)
            for t in r:
                text += t
                chat_box.update_msg(text)
            chat_box.update_msg(text, streaming=False) # 更新最终的字符串，去除光标
        elif dialogue_mode == "知识库问答":
            chat_box.ai_say(f"正在查询知识库： `{selected_kb}` ...")
            text = ""
            for t in api.knowledge_base_chat(prompt, selected_kb):
                text += t
                chat_box.update_msg(text)
            chat_box.update_msg(text, streaming=False)
        elif dialogue_mode == "Bing 搜索问答":
            chat_box.ai_say("正在执行Bing搜索...")
            text = ""
            for t in api.bing_search_chat(prompt):
                text += t
                chat_box.update_msg(text)
            chat_box.update_msg(text, streaming=False)
        elif dialogue_mode == "Duck 搜索问答":
            chat_box.ai_say("正在执行Duckduck搜索...")
            text = ""
            for t in api.duckduckgo_search_chat(prompt):
                text += t
                chat_box.update_msg(text)
            chat_box.update_msg(text, streaming=False)

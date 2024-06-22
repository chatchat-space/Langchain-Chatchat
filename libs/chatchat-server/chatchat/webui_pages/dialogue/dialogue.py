import base64
import os
import uuid
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlencode

# from audio_recorder_streamlit import audio_recorder
import openai
import streamlit as st
import streamlit_antd_components as sac
from streamlit_chatbox import *
from streamlit_extras.bottom_container import bottom

from chatchat.configs import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_LLM_MODEL,
    LLM_MODEL_CONFIG,
    MODEL_PLATFORMS,
    TEMPERATURE,
)
from chatchat.server.callback_handler.agent_callback_handler import AgentStatus
from chatchat.server.knowledge_base.model.kb_document_model import DocumentWithVSId
from chatchat.server.utils import MsgType, get_config_models
from chatchat.webui_pages.dialogue.utils import process_files
from chatchat.webui_pages.utils import *

chat_box = ChatBox(assistant_avatar=get_img_base64("chatchat_icon_blue_square_v2.png"))


def save_session(conv_name: str = None):
    """save session state to chat context"""
    chat_box.context_from_session(
        conv_name, exclude=["selected_page", "prompt", "cur_conv_name"]
    )


def restore_session(conv_name: str = None):
    """restore sesstion state from chat context"""
    chat_box.context_to_session(
        conv_name, exclude=["selected_page", "prompt", "cur_conv_name"]
    )


def rerun():
    """
    save chat context before rerun
    """
    save_session()
    st.rerun()


def get_messages_history(
    history_len: int, content_in_expander: bool = False
) -> List[Dict]:
    """
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    """

    def filter(msg):
        content = [
            x for x in msg["elements"] if x._output_method in ["markdown", "text"]
        ]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    messages = chat_box.filter_history(history_len=history_len, filter=filter)
    if sys_msg := st.session_state.get("system_message"):
        messages = [{"role": "system", "content": sys_msg}] + messages
    return messages


@st.cache_data
def upload_temp_docs(files, _api: ApiRequest) -> str:
    """
    将文件上传到临时目录，用于文件对话
    返回临时向量库ID
    """
    return _api.upload_temp_docs(files).get("data", {}).get("id")


def add_conv(name: str = ""):
    conv_names = chat_box.get_chat_names()
    if not name:
        i = len(conv_names) + 1
        while True:
            name = f"会话{i}"
            if name not in conv_names:
                break
            i += 1
    if name in conv_names:
        sac.alert(
            "创建新会话出错",
            f"该会话名称 “{name}” 已存在",
            color="error",
            closable=True,
        )
    else:
        chat_box.use_chat_name(name)
        st.session_state["cur_conv_name"] = name


def del_conv(name: str = None):
    conv_names = chat_box.get_chat_names()
    name = name or chat_box.cur_chat_name
    if len(conv_names) == 1:
        sac.alert(
            "删除会话出错", f"这是最后一个会话，无法删除", color="error", closable=True
        )
    elif not name or name not in conv_names:
        sac.alert(
            "删除会话出错", f"无效的会话名称：“{name}”", color="error", closable=True
        )
    else:
        chat_box.del_chat_name(name)
        restore_session()
        st.session_state["cur_conv_name"] = chat_box.cur_chat_name


def clear_conv(name: str = None):
    chat_box.reset_history(name=name or None)


# @st.cache_data
def list_tools(_api: ApiRequest):
    return _api.list_tools()


def dialogue_page(
    api: ApiRequest,
    is_lite: bool = False,
):
    ctx = chat_box.context
    ctx.setdefault("uid", uuid.uuid4().hex)
    ctx.setdefault("file_chat_id", None)
    ctx.setdefault("llm_model", DEFAULT_LLM_MODEL)
    ctx.setdefault("temperature", TEMPERATURE)
    st.session_state.setdefault("cur_conv_name", chat_box.cur_chat_name)
    st.session_state.setdefault("last_conv_name", chat_box.cur_chat_name)

    # sac on_change callbacks not working since st>=1.34
    if st.session_state.cur_conv_name != st.session_state.last_conv_name:
        save_session(st.session_state.last_conv_name)
        restore_session(st.session_state.cur_conv_name)
        st.session_state.last_conv_name = st.session_state.cur_conv_name

    # st.write(chat_box.cur_chat_name)
    # st.write(st.session_state)

    @st.experimental_dialog("模型配置", width="large")
    def llm_model_setting():
        # 模型
        cols = st.columns(3)
        platforms = ["所有"] + [x["platform_name"] for x in MODEL_PLATFORMS]
        platform = cols[0].selectbox("选择模型平台", platforms, key="platform")
        llm_models = list(
            get_config_models(
                model_type="llm", platform_name=None if platform == "所有" else platform
            )
        )
        llm_model = cols[1].selectbox("选择LLM模型", llm_models, key="llm_model")
        temperature = cols[2].slider("Temperature", 0.0, 1.0, key="temperature")
        system_message = st.text_area("System Message:", key="system_message")
        if st.button("OK"):
            rerun()

    @st.experimental_dialog("重命名会话")
    def rename_conversation():
        name = st.text_input("会话名称")
        if st.button("OK"):
            chat_box.change_chat_name(name)
            restore_session()
            st.session_state["cur_conv_name"] = name
            rerun()

    with st.sidebar:
        tab1, tab2 = st.tabs(["工具设置", "会话设置"])

        with tab1:
            use_agent = st.checkbox(
                "启用Agent", help="请确保选择的模型具备Agent能力", key="use_agent"
            )
            # 选择工具
            tools = list_tools(api)
            tool_names = ["None"] + list(tools)
            if use_agent:
                # selected_tools = sac.checkbox(list(tools), format_func=lambda x: tools[x]["title"], label="选择工具",
                # check_all=True, key="selected_tools")
                selected_tools = st.multiselect(
                    "选择工具",
                    list(tools),
                    format_func=lambda x: tools[x]["title"],
                    key="selected_tools",
                )
            else:
                # selected_tool = sac.buttons(list(tools), format_func=lambda x: tools[x]["title"], label="选择工具",
                # key="selected_tool")
                selected_tool = st.selectbox(
                    "选择工具",
                    tool_names,
                    format_func=lambda x: tools.get(x, {"title": "None"})["title"],
                    key="selected_tool",
                )
                selected_tools = [selected_tool]
            selected_tool_configs = {
                name: tool["config"]
                for name, tool in tools.items()
                if name in selected_tools
            }

            if "None" in selected_tools:
                selected_tools.remove("None")
            # 当不启用Agent时，手动生成工具参数
            # TODO: 需要更精细的控制控件
            tool_input = {}
            if not use_agent and len(selected_tools) == 1:
                with st.expander("工具参数", True):
                    for k, v in tools[selected_tools[0]]["args"].items():
                        if choices := v.get("choices", v.get("enum")):
                            tool_input[k] = st.selectbox(v["title"], choices)
                        else:
                            if v["type"] == "integer":
                                tool_input[k] = st.slider(
                                    v["title"], value=v.get("default")
                                )
                            elif v["type"] == "number":
                                tool_input[k] = st.slider(
                                    v["title"], value=v.get("default"), step=0.1
                                )
                            else:
                                tool_input[k] = st.text_input(
                                    v["title"], v.get("default")
                                )

            # uploaded_file = st.file_uploader("上传附件", accept_multiple_files=False)
            # files_upload = process_files(files=[uploaded_file]) if uploaded_file else None
            files_upload = None

        with tab2:
            # 会话
            cols = st.columns(3)
            conv_names = chat_box.get_chat_names()

            def on_conv_change():
                print(conversation_name, st.session_state.cur_conv_name)
                save_session(conversation_name)
                restore_session(st.session_state.cur_conv_name)

            conversation_name = sac.buttons(
                conv_names,
                label="当前会话：",
                key="cur_conv_name",
                on_change=on_conv_change,
            )
            chat_box.use_chat_name(conversation_name)
            conversation_id = chat_box.context["uid"]
            if cols[0].button("新建", on_click=add_conv):
                ...
            if cols[1].button("重命名"):
                rename_conversation()
            if cols[2].button("删除", on_click=del_conv):
                ...

    # Display chat messages from history on app rerun
    chat_box.output_messages()
    chat_input_placeholder = "请输入对话内容，换行请使用Shift+Enter。"

    # def on_feedback(
    #         feedback,
    #         message_id: str = "",
    #         history_index: int = -1,
    # ):

    #     reason = feedback["text"]
    #     score_int = chat_box.set_feedback(feedback=feedback, history_index=history_index)
    #     api.chat_feedback(message_id=message_id,
    #                       score=score_int,
    #                       reason=reason)
    #     st.session_state["need_rerun"] = True

    # feedback_kwargs = {
    #     "feedback_type": "thumbs",
    #     "optional_text_label": "欢迎反馈您打分的理由",
    # }

    #  传入后端的内容
    chat_model_config = {key: {} for key in LLM_MODEL_CONFIG.keys()}
    for key in LLM_MODEL_CONFIG:
        if LLM_MODEL_CONFIG[key]:
            first_key = next(iter(LLM_MODEL_CONFIG[key]))
            chat_model_config[key][first_key] = LLM_MODEL_CONFIG[key][first_key]
    llm_model = ctx.get("llm_model")
    if llm_model is not None:
        chat_model_config["llm_model"][llm_model] = LLM_MODEL_CONFIG["llm_model"].get(
            llm_model, {}
        )

    # chat input
    with bottom():
        cols = st.columns([1, 1, 15])
        if cols[0].button(":atom_symbol:"):
            widget_keys = ["platform", "llm_model", "temperature", "system_message"]
            chat_box.context_to_session(include=widget_keys)
            llm_model_setting()
        # with cols[1]:
        #     mic_audio = audio_recorder("", icon_size="2x", key="mic_audio")
        prompt = cols[2].chat_input(chat_input_placeholder, key="prompt")
    if prompt:
        history = get_messages_history(
            chat_model_config["llm_model"]
            .get(next(iter(chat_model_config["llm_model"])), {})
            .get("history_len", 1)
        )
        chat_box.user_say(prompt)
        if files_upload:
            if files_upload["images"]:
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{files_upload["images"][0]}" width="300">',
                    unsafe_allow_html=True,
                )
            elif files_upload["videos"]:
                st.markdown(
                    f'<video width="400" height="300" controls><source src="data:video/mp4;base64,{files_upload["videos"][0]}" type="video/mp4"></video>',
                    unsafe_allow_html=True,
                )
            elif files_upload["audios"]:
                st.markdown(
                    f'<audio controls><source src="data:audio/wav;base64,{files_upload["audios"][0]}" type="audio/wav"></audio>',
                    unsafe_allow_html=True,
                )

        chat_box.ai_say("正在思考...")
        text = ""
        started = False

        client = openai.Client(base_url=f"{api_address()}/chat", api_key="NONE")
        messages = history + [{"role": "user", "content": prompt}]
        tools = list(selected_tool_configs)
        if len(selected_tools) == 1:
            tool_choice = selected_tools[0]
        else:
            tool_choice = None
        # 如果 tool_input 中有空的字段，设为用户输入
        for k in tool_input:
            if tool_input[k] in [None, ""]:
                tool_input[k] = prompt

        extra_body = dict(
            metadata=files_upload,
            chat_model_config=chat_model_config,
            conversation_id=conversation_id,
            tool_input=tool_input,
        )
        for d in client.chat.completions.create(
            messages=messages,
            model=llm_model,
            stream=True,
            tools=tools or openai.NOT_GIVEN,
            tool_choice=tool_choice,
            extra_body=extra_body,
        ):
            # from pprint import pprint
            # pprint(d)
            message_id = d.message_id
            metadata = {
                "message_id": message_id,
            }

            # clear initial message
            if not started:
                chat_box.update_msg("", streaming=False)
                started = True

            if d.status == AgentStatus.error:
                st.error(d.choices[0].delta.content)
            elif d.status == AgentStatus.llm_start:
                chat_box.insert_msg("正在解读工具输出结果...")
                text = d.choices[0].delta.content or ""
            elif d.status == AgentStatus.llm_new_token:
                text += d.choices[0].delta.content or ""
                chat_box.update_msg(
                    text.replace("\n", "\n\n"), streaming=True, metadata=metadata
                )
            elif d.status == AgentStatus.llm_end:
                text += d.choices[0].delta.content or ""
                chat_box.update_msg(
                    text.replace("\n", "\n\n"), streaming=False, metadata=metadata
                )
            # tool 的输出与 llm 输出重复了
            # elif d.status == AgentStatus.tool_start:
            #     formatted_data = {
            #         "Function": d.choices[0].delta.tool_calls[0].function.name,
            #         "function_input": d.choices[0].delta.tool_calls[0].function.arguments,
            #     }
            #     formatted_json = json.dumps(formatted_data, indent=2, ensure_ascii=False)
            #     text = """\n```{}\n```\n""".format(formatted_json)
            #     chat_box.insert_msg( # TODO: insert text directly not shown
            #         Markdown(text, title="Function call", in_expander=True, expanded=True, state="running"))
            # elif d.status == AgentStatus.tool_end:
            #     tool_output = d.choices[0].delta.tool_calls[0].tool_output
            #     if d.message_type == MsgType.IMAGE:
            #         for url in json.loads(tool_output).get("images", []):
            #             url = f"{api.base_url}/media/{url}"
            #             chat_box.insert_msg(Image(url))
            #         chat_box.update_msg(expanded=False, state="complete")
            #     else:
            #         text += """\n```\nObservation:\n{}\n```\n""".format(tool_output)
            #         chat_box.update_msg(text, streaming=False, expanded=False, state="complete")
            elif d.status == AgentStatus.agent_finish:
                text = d.choices[0].delta.content or ""
                chat_box.update_msg(text.replace("\n", "\n\n"))
            elif d.status is None:  # not agent chat
                if getattr(d, "is_ref", False):
                    context = ""
                    docs = d.tool_output.get("docs")
                    source_documents = []
                    for inum, doc in enumerate(docs):
                        doc = DocumentWithVSId.parse_obj(doc)
                        filename = doc.metadata.get("source")
                        parameters = urlencode(
                            {
                                "knowledge_base_name": d.tool_output.get(
                                    "knowledge_base"
                                ),
                                "file_name": filename,
                            }
                        )
                        url = (
                            f"{api.base_url}/knowledge_base/download_doc?" + parameters
                        )
                        ref = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
                        source_documents.append(ref)
                    context = "\n".join(source_documents)
                    chat_box.insert_msg(
                        Markdown(
                            context,
                            in_expander=True,
                            state="complete",
                            title="参考资料",
                        )
                    )
                    chat_box.insert_msg("")
                else:
                    text += d.choices[0].delta.content or ""
                    chat_box.update_msg(
                        text.replace("\n", "\n\n"), streaming=True, metadata=metadata
                    )
        chat_box.update_msg(text, streaming=False, metadata=metadata)

        if os.path.exists("tmp/image.jpg"):
            with open("tmp/image.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                img_tag = (
                    f'<img src="data:image/jpeg;base64,{encoded_string}" width="300">'
                )
                st.markdown(img_tag, unsafe_allow_html=True)
            os.remove("tmp/image.jpg")
        # chat_box.show_feedback(**feedback_kwargs,
        #                        key=message_id,
        #                        on_submit=on_feedback,
        #                        kwargs={"message_id": message_id, "history_index": len(chat_box.history) - 1})

        # elif dialogue_mode == "文件对话":
        #     if st.session_state["file_chat_id"] is None:
        #         st.error("请先上传文件再进行对话")
        #         st.stop()
        #     chat_box.ai_say([
        #         f"正在查询文件 `{st.session_state['file_chat_id']}` ...",
        #         Markdown("...", in_expander=True, title="文件匹配结果", state="complete"),
        #     ])
        #     text = ""
        #     for d in api.file_chat(prompt,
        #                            knowledge_id=st.session_state["file_chat_id"],
        #                            top_k=kb_top_k,
        #                            score_threshold=score_threshold,
        #                            history=history,
        #                            model=llm_model,
        #                            prompt_name=prompt_template_name,
        #                            temperature=temperature):
        #         if error_msg := check_error_msg(d):
        #             st.error(error_msg)
        #         elif chunk := d.get("answer"):
        #             text += chunk
        #             chat_box.update_msg(text, element_index=0)
        #     chat_box.update_msg(text, element_index=0, streaming=False)
        #     chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)

    now = datetime.now()
    with tab2:
        cols = st.columns(2)
        export_btn = cols[0]
        if cols[1].button(
            "清空对话",
            use_container_width=True,
        ):
            chat_box.reset_history()
            rerun()

    export_btn.download_button(
        "导出记录",
        "".join(chat_box.export2md()),
        file_name=f"{now:%Y-%m-%d %H.%M}_对话记录.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # st.write(chat_box.context)

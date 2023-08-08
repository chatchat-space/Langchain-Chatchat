from pydoc import Helper
import streamlit as st
from webui_pages.utils import *
import streamlit_antd_components as sac
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path
from streamlit_chatbox import *


SENTENCE_SIZE = 100


def knowledge_base_page(api: ApiRequest):
    api = ApiRequest(base_url="http://127.0.0.1:7861", no_remote_api=True)
    chat_box = ChatBox(session_key="kb_messages")

    kb_list = api.list_knowledge_bases()
    kb_docs = {}
    for kb in kb_list:
        kb_docs[kb] = api.list_kb_docs(kb)

    with st.sidebar:
        def on_new_kb():
            if name := st.session_state.get("new_kb_name"):
                if name in kb_list:
                    st.error(f"名为 {name} 的知识库已经存在！")
                else:
                    ret = api.create_knowledge_base(name)
                    st.toast(ret["msg"])

        def on_del_kb():
            if name := st.session_state.get("new_kb_name"):
                if name in kb_list:
                    ret = api.delete_knowledge_base(name)
                    st.toast(ret["msg"])
                else:
                    st.error(f"名为 {name} 的知识库不存在！")
            
        cols = st.columns([2, 1, 1])
        new_kb_name = cols[0].text_input(
            "新知识库名称",
            placeholder="新知识库名称",
            label_visibility="collapsed",
            key="new_kb_name",
        )
        cols[1].button("新建", on_click=on_new_kb, disabled=not bool(new_kb_name))
        cols[2].button("删除", on_click=on_del_kb, disabled=not bool(new_kb_name))

        st.write("知识库：")
        if kb_list:
            try:
                index = kb_list.index(st.session_state.get("cur_kb"))
            except:
                index = 0
            kb = sac.buttons(
                kb_list,
                index,
                format_func=lambda x: f"{x} ({len(kb_docs[x])})",
            )
            st.session_state["cur_kb"] = kb
            sentence_size = st.slider("文本入库分句长度限制", 1, 1000, SENTENCE_SIZE, disabled=True)
            files = st.file_uploader("上传知识文件",
                                    ["docx", "txt", "md", "csv", "xlsx", "pdf"],
                                    accept_multiple_files=True,
                                    key="files",
                                    )
            if st.button(
                "添加文件到知识库",
                help="请先上传文件，再点击添加",
                use_container_width=True,
                disabled=len(files)==0,
            ):
                for f in files:
                    ret = api.upload_kb_doc(f, kb)
                    if ret["code"] == 200:
                        st.toast(ret["msg"], icon="✔")
                    else:
                        st.toast(ret["msg"], icon="❌")
                st.session_state.files = []

            if st.button(
                "重建知识库",
                help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
                use_container_width=True,
                disabled=True,
            ):
                progress = st.progress(0.0, "")
                for d in api.recreate_vector_store(kb):
                    progress.progress(d["finished"] / d["total"], f"正在处理： {d['doc']}")

    if kb_list:
        # 知识库详情
        st.subheader(f"知识库 {kb} 详情")
        df = pd.DataFrame([[i + 1, x] for i, x in enumerate(kb_docs[kb])], columns=["No", "文档名称"])
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_column("No", width=50)
        gb.configure_selection()

        cols = st.columns([1, 2])

        with cols[0]:
            docs = AgGrid(df, gb.build())
        
        with cols[1]:
            cols = st.columns(3)
            selected_rows = docs.get("selected_rows", [])

            cols = st.columns([2, 3, 2])
            if selected_rows:
                file_name = selected_rows[0]["文档名称"]
                file_path = get_file_path(kb, file_name)
                with open(file_path, "rb") as fp:
                    cols[0].download_button("下载选中文档", fp, file_name=file_name)
            else:
                cols[0].download_button("下载选中文档", "", disabled=True)
            if cols[2].button("删除选中文档！", type="primary"):
                for row in selected_rows:
                    ret = api.delete_kb_doc(kb, row["文档名称"])
                    st.toast(ret["msg"])
                st.experimental_rerun()

            st.write("本文档包含以下知识条目：(待定内容)")

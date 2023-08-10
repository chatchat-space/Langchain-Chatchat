import streamlit as st
from webui_pages.utils import *
# import streamlit_antd_components as sac
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path
# from streamlit_chatbox import *
from typing import Literal, Dict, Tuple


SENTENCE_SIZE = 100


def config_aggrid(
    df: pd.DataFrame,
    columns: Dict[Tuple[str, str], Dict] = {},
    selection_mode: Literal["single", "multiple", "disabled"] = "single",
    use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("No", width=40)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode,
        use_checkbox,
        # pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    return gb


# kb_box = ChatBox(session_key="kb_messages")

def knowledge_base_page(api: ApiRequest):
    api = ApiRequest(base_url="http://127.0.0.1:7861", no_remote_api=True)
    kb_details = get_kb_details(api)
    kb_list = list(kb_details.kb_name)

    cols = st.columns([2, 1, 1])
    new_kb_name = cols[0].text_input(
        "新知识库名称",
        placeholder="新知识库名称",
        label_visibility="collapsed",
        key="new_kb_name",
    )

    if cols[1].button("新建", disabled=not bool(new_kb_name)) and new_kb_name:
        if new_kb_name in kb_list:
            st.error(f"名为 {new_kb_name} 的知识库已经存在！")
        else:
            ret = api.create_knowledge_base(new_kb_name)
            st.toast(ret["msg"])
            st.experimental_rerun()

    if cols[2].button("删除", disabled=not bool(new_kb_name)) and new_kb_name:
        if new_kb_name in kb_list:
            ret = api.delete_knowledge_base(new_kb_name)
            st.toast(ret["msg"])
            st.experimental_rerun()
        else:
            st.error(f"名为 {new_kb_name} 的知识库不存在！")

    st.write("知识库列表：")
    if kb_list:
        gb = config_aggrid(
            kb_details,
            {
                ("kb_name", "知识库名称"): {"maxWidth": 150},
                ("vs_type", "知识库类型"): {"maxWidth": 100},
                ("embed_model", "嵌入模型"): {"maxWidth": 100},
                ("file_count", "文档数量"): {"maxWidth": 60},
                ("create_time", "创建时间"): {"maxWidth": 150},
                ("in_folder", "文件夹"): {"maxWidth": 50},
                ("in_db", "数据库"): {"maxWidth": 50},
            }
        )
        kb_grid = AgGrid(kb_details, gb.build())
        # st.write(kb_grid)
        if kb_grid.selected_rows:
            # st.session_state.selected_rows = [x["nIndex"] for x in kb_grid.selected_rows]
            kb = kb_grid.selected_rows[0]["kb_name"]

            with st.sidebar:
                sentence_size = st.slider("文本入库分句长度限制", 1, 1000, SENTENCE_SIZE, disabled=True)
                files = st.file_uploader("上传知识文件",
                                        ["docx", "txt", "md", "csv", "xlsx", "pdf"],
                                        accept_multiple_files=True,
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
                        progress.progress(d["finished"] / d["t]otal"], f"正在处理： {d['doc']}")

            # 知识库详情
            st.write(f"知识库 {kb} 详情:")
            doc_details = get_kb_doc_details(api, kb)
            doc_details.drop(columns=["kb_name"], inplace=True)

            gb = config_aggrid(
                doc_details,
                {
                    ("file_name", "文档名称"): {"maxWidth": 150},
                    ("file_ext", "文档类型"): {"maxWidth": 50},
                    ("file_version", "文档版本"): {"maxWidth": 50},
                    ("document_loader", "文档加载器"): {"maxWidth": 150},
                    ("text_splitter", "分词器"): {"maxWidth": 150},
                    ("create_time", "创建时间"): {"maxWidth": 150},
                    ("in_folder", "文件夹"): {"maxWidth": 50},
                    ("in_db", "数据库"): {"maxWidth": 50},
                },
                "multiple",
            )

            doc_grid = AgGrid(doc_details, gb.build())
            
            cols = st.columns(3)
            selected_rows = doc_grid.get("selected_rows", [])

            cols = st.columns(4)
            if selected_rows:
                file_name = selected_rows[0]["file_name"]
                file_path = get_file_path(kb, file_name)
                with open(file_path, "rb") as fp:
                    cols[0].download_button("下载选中文档", fp, file_name=file_name)
            else:
                cols[0].download_button("下载选中文档", "", disabled=True)
            
            if cols[1].button("入库", disabled=len(selected_rows)==0):
                for row in selected_rows:
                    api.update_kb_doc(kb, row["file_name"])
                st.experimental_rerun()

            if cols[2].button("出库", disabled=len(selected_rows)==0):
                for row in selected_rows:
                    api.delete_kb_doc(kb, row["file_name"])
                st.experimental_rerun()

            if cols[3].button("删除选中文档！", type="primary"):
                for row in selected_rows:
                    ret = api.delete_kb_doc(kb, row["file_name"], True)
                    st.toast(ret["msg"])
                st.experimental_rerun()

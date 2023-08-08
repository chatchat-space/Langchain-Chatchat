import streamlit as st
from webui_pages.utils import *
# import streamlit_antd_components as sac
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path, list_kbs_from_folder, list_docs_from_folder
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.db.repository.knowledge_base_repository import get_kb_detail
from server.db.repository.knowledge_file_repository import get_file_detail
# from streamlit_chatbox import *
from typing import Literal, Dict


SENTENCE_SIZE = 100


def get_kb_details(api: ApiRequest) -> pd.DataFrame:
    kbs_in_folder = list_kbs_from_folder()
    kbs_in_db = api.list_knowledge_bases()
    result = {}

    for kb in kbs_in_folder:
        result[kb] = {
            "kb_name": kb,
            "vs_type": "",
            "embed_model": "",
            "file_count": 0,
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }
    
    for kb in kbs_in_db:
        kb_detail = get_kb_detail(kb)
        if kb_detail:
            kb_detail["in_db"] = True
            if kb in result:
                result[kb].update(kb_detail)
            else:
                kb_detail["in_folder"] = False
                result[kb] = kb_detail

    df = pd.DataFrame(result.values())
    df.insert(0, "No", range(1, len(df) + 1))
    return df


def get_kb_doc_details(api: ApiRequest, kb: str) -> pd.DataFrame:
    docs_in_folder = list_docs_from_folder(kb)
    docs_in_db = api.list_kb_docs(kb)
    result = {}

    for doc in docs_in_folder:
        result[doc] = {
            "kb_name": kb,
            "file_name": doc,
            "file_ext": os.path.splitext(doc)[-1],
            "file_version": 0,
            "document_loader": "",
            "text_splitter": "",
            "create_time": None,
            "in_folder": True,
            "in_db": False,
        }
    
    for doc in docs_in_db:
        doc_detail = get_file_detail(kb, doc)
        if doc_detail:
            doc_detail["in_db"] = True
            if doc in result:
                result[doc].update(doc_detail)
            else:
                doc_detail["in_folder"] = False
                result[doc] = doc_detail

    df = pd.DataFrame(result.values())
    df.insert(0, "No", range(1, len(df) + 1))
    return df


def config_aggrid(
    df: pd.DataFrame,
    titles: Dict[str, str] = {},
    selection_mode: Literal["single", "multiple", "disabled"] = "single",
    use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("No", width=50)
    for k, v in titles.items():
        gb.configure_column(k, v, maxWidth=100)
    gb.configure_selection(selection_mode, use_checkbox, pre_selected_rows=[0])
    return gb


# kb_box = ChatBox(session_key="kb_messages")

def knowledge_base_page(api: ApiRequest):
    api = ApiRequest(base_url="http://127.0.0.1:7861", no_remote_api=True)
    kb_details = get_kb_details(api)
    kb_list = list(kb_details.keys())

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
        gb = config_aggrid(
            kb_details,
            {
                "kb_name": "知识库名称",
                "vs_type": "知识库类型",
                "embed_model": "嵌入模型",
                "file_count": "文档数量",
                "create_time": "创建时间",
                "in_folder": "存在于文件夹",
                "in_db": "存在于数据库",
            }
        )
        kb_grid = AgGrid(kb_details, gb.build())
        if kb_grid.selected_rows:
            kb = kb_grid.selected_rows[0]["kb_name"]

            with st.sidebar:
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
                        progress.progress(d["finished"] / d["t]otal"], f"正在处理： {d['doc']}")

            # 知识库详情
            st.subheader(f"知识库 {kb} 详情")
            doc_details = get_kb_doc_details(api, kb)
            del doc_details["kb_name"]
            gb = config_aggrid(
                doc_details,
                {
                    "file_name": "文档名称",
                    "file_ext": "文档类型",
                    "file_version": "文档版本",
                    "document_loader": "文档加载器",
                    "text_splitter": "分词器",
                    "create_time": "创建时间",
                    "in_folder": "存在于文件夹",
                    "in_db": "存在于数据库",
                },
                "multiple",
            )

            doc_grid = AgGrid(doc_details, gb.build())
            
            cols = st.columns(3)
            selected_rows = doc_grid.get("selected_rows", [])

            cols = st.columns([2, 3, 2])
            if selected_rows:
                file_name = selected_rows[0]["file_name"]
                file_path = get_file_path(kb, file_name)
                with open(file_path, "rb") as fp:
                    cols[0].download_button("下载选中文档", fp, file_name=file_name)
            else:
                cols[0].download_button("下载选中文档", "", disabled=True)
            if cols[2].button("删除选中文档！", type="primary"):
                for row in selected_rows:
                    ret = api.delete_kb_doc(kb, row["file_name"])
                    st.toast(ret["msg"])
                st.experimental_rerun()

            st.write("本文档包含以下知识条目：(待定内容)")

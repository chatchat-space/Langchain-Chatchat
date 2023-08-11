from pydoc import doc
import streamlit as st
from webui_pages.utils import *
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from server.knowledge_base.utils import get_file_path, LOADER_DICT
from server.knowledge_base.kb_service.base import get_kb_details, get_kb_doc_details
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


def knowledge_base_page(api: ApiRequest):
    # api = ApiRequest(base_url="http://127.0.0.1:7861", no_remote_api=True)
    kb_list = get_kb_details()

    cols = st.columns([3, 1, 1, 3])
    new_kb_name = cols[0].text_input(
        "新知识库名称",
        placeholder="新知识库名称，不支持中文命名",
        label_visibility="collapsed",
        key="new_kb_name",
    )

    if cols[1].button(
            "新建",
            disabled=not bool(new_kb_name),
            use_container_width=True,
    ) and new_kb_name:
        if new_kb_name in kb_list:
            st.error(f"名为 {new_kb_name} 的知识库已经存在！")
        else:
            ret = api.create_knowledge_base(new_kb_name)
            st.toast(ret["msg"])
            st.experimental_rerun()

    if cols[2].button(
            "删除",
            disabled=not bool(new_kb_name),
            use_container_width=True,
    ) and new_kb_name:
        if new_kb_name in kb_list:
            ret = api.delete_knowledge_base(new_kb_name)
            st.toast(ret["msg"])
            st.experimental_rerun()
        else:
            st.error(f"名为 {new_kb_name} 的知识库不存在！")

    selected_kb = cols[3].selectbox(
        "请选择知识库：",
        kb_list,
        format_func=lambda s: f"{s['kb_name']} ({s['vs_type']} @ {s['embed_model']})",
        label_visibility="collapsed"
    )

    if selected_kb:
        kb = selected_kb["kb_name"]

        # 知识库详情
        st.write(f"知识库 `{kb}` 详情:")
        # st.info("请选择文件，点击按钮进行操作。")
        doc_details = pd.DataFrame(get_kb_doc_details(kb))
        doc_details.drop(columns=["kb_name"], inplace=True)
        doc_details = doc_details[[
            "No", "file_name", "document_loader", "text_splitter", "in_folder", "in_db",
        ]]

        gb = config_aggrid(
            doc_details,
            {
                ("file_name", "文档名称"): {},
                # ("file_ext", "文档类型"): {},
                # ("file_version", "文档版本"): {},
                ("document_loader", "文档加载器"): {},
                ("text_splitter", "分词器"): {},
                # ("create_time", "创建时间"): {},
                ("in_folder", "文件夹"): {},
                ("in_db", "数据库"): {},
            },
            "multiple",
        )

        doc_grid = AgGrid(
            doc_details,
            gb.build(),
            columns_auto_size_mode="FIT_CONTENTS",
            theme="alpine",
            custom_css={
                "#gridToolBar": {"display": "none"},
            },
        )

        cols = st.columns(3)
        selected_rows = doc_grid.get("selected_rows", [])

        cols = st.columns(4)
        if selected_rows:
            file_name = selected_rows[0]["file_name"]
            file_path = get_file_path(kb, file_name)
            with open(file_path, "rb") as fp:
                cols[0].download_button(
                    "下载选中文档",
                    fp,
                    file_name=file_name,
                    use_container_width=True,)
        else:
            cols[0].download_button(
                "下载选中文档",
                "",
                disabled=True,
                use_container_width=True,)

        if cols[1].button(
                "入库",
                disabled=len(selected_rows) == 0,
                use_container_width=True,
                help="将文件分词并加载到向量库中",
        ):
            for row in selected_rows:
                api.update_kb_doc(kb, row["file_name"])
            st.experimental_rerun()

        if cols[2].button(
                "出库",
                disabled=len(selected_rows) == 0,
                use_container_width=True,
                help="将文件从向量库中删除，但不删除文件本身。"
        ):
            for row in selected_rows:
                api.delete_kb_doc(kb, row["file_name"])
            st.experimental_rerun()

        if cols[3].button(
                "删除选中文档！",
                type="primary",
                use_container_width=True,
        ):
            for row in selected_rows:
                ret = api.delete_kb_doc(kb, row["file_name"], True)
                st.toast(ret["msg"])
            st.experimental_rerun()

        st.divider()
        # sentence_size = st.slider("文本入库分句长度限制", 1, 1000, SENTENCE_SIZE, disabled=True)
        files = st.file_uploader("上传知识文件",
                                [i for ls in LOADER_DICT.values() for i in ls],
                                accept_multiple_files=True,
                                )
        cols = st.columns([3, 1])
        if cols[0].button(
                "添加文件到知识库",
                help="请先上传文件，再点击添加",
                use_container_width=True,
                disabled=len(files) == 0,
        ):
            for f in files:
                ret = api.upload_kb_doc(f, kb)
                if ret["code"] == 200:
                    st.toast(ret["msg"], icon="✔")
                else:
                    st.toast(ret["msg"], icon="❌")
            st.session_state.files = []

        # todo: freezed
        # if cols[1].button(
        #         "重建知识库",
        #         help="无需上传文件，通过其它方式将文档拷贝到对应知识库content目录下，点击本按钮即可重建知识库。",
        #         use_container_width=True,
        #         type="primary",
        # ):
        #     progress = st.progress(0.0, "")
        #     for d in api.recreate_vector_store(kb):
        #         progress.progress(d["finished"] / d["total"], f"正在处理： {d['doc']}")

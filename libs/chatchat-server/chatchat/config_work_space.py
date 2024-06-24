import ast
import json

# We cannot lazy-load click here because its used via decorators.
import click

from chatchat.configs import (
    config_basic_workspace,
    config_kb_workspace,
    config_model_workspace,
    config_server_workspace,
)


@click.group(help="指令` chatchat-config` 工作空间配置")
def main():
    pass


@main.command("basic", help="基础配置")
@click.option(
    "--verbose", type=click.Choice(["true", "false"]), help="是否开启详细日志"
)
@click.option("--data", help="初始化数据存放路径，注意：目录会清空重建")
@click.option("--format", help="日志格式")
@click.option("--clear", is_flag=True, help="清除配置")
@click.option("--show", is_flag=True, help="显示配置")
def basic(**kwargs):
    if kwargs["verbose"]:
        if kwargs["verbose"].lower() == "true":
            config_basic_workspace.set_log_verbose(True)
        else:
            config_basic_workspace.set_log_verbose(False)
    if kwargs["data"]:
        config_basic_workspace.set_data_path(kwargs["data"])
    if kwargs["format"]:
        config_basic_workspace.set_log_format(kwargs["format"])
    if kwargs["clear"]:
        config_basic_workspace.clear()
    if kwargs["show"]:
        print(config_basic_workspace.get_config())


@main.command("model", help="模型配置")
@click.option("--default_llm_model", help="默认llm模型")
@click.option("--default_embedding_model", help="默认embedding模型")
@click.option("--agent_model", help="agent模型")
@click.option("--history_len", type=int, help="历史长度")
@click.option("--max_tokens", type=int, help="最大tokens")
@click.option("--temperature", type=float, help="温度")
@click.option("--support_agent_models", multiple=True, help="支持的agent模型")
@click.option(
    "--set_model_platforms",
    type=str,
    help="""模型平台配置
                                                                    as a JSON string. 
                                                                    """,
)
@click.option(
    "--set_tool_config",
    type=str,
    help="""
                                                            工具配置项  as a JSON string.
                                                            """,
)
@click.option("--clear", is_flag=True, help="清除配置")
@click.option("--show", is_flag=True, help="显示配置")
def model(**kwargs):
    if kwargs["default_llm_model"]:
        config_model_workspace.set_default_llm_model(
            llm_model=kwargs["default_llm_model"]
        )
    if kwargs["default_embedding_model"]:
        config_model_workspace.set_default_embedding_model(
            embedding_model=kwargs["default_embedding_model"]
        )

    if kwargs["agent_model"]:
        config_model_workspace.set_agent_model(agent_model=kwargs["agent_model"])

    if kwargs["history_len"]:
        config_model_workspace.set_history_len(history_len=kwargs["history_len"])

    if kwargs["max_tokens"]:
        config_model_workspace.set_max_tokens(max_tokens=kwargs["max_tokens"])

    if kwargs["temperature"]:
        config_model_workspace.set_temperature(temperature=kwargs["temperature"])

    if kwargs["support_agent_models"]:
        config_model_workspace.set_support_agent_models(
            support_agent_models=kwargs["support_agent_models"]
        )
    if kwargs["set_model_platforms"]:
        model_platforms_dict = json.loads(kwargs["set_model_platforms"])
        config_model_workspace.set_model_platforms(model_platforms=model_platforms_dict)
    if kwargs["set_tool_config"]:
        tool_config_dict = json.loads(kwargs["set_tool_config"])
        config_model_workspace.set_tool_config(tool_config=tool_config_dict)

    if kwargs["clear"]:
        config_model_workspace.clear()
    if kwargs["show"]:
        print(config_model_workspace.get_config())


@main.command("server", help="服务配置")
@click.option("--httpx_default_timeout", type=int, help="httpx默认超时时间")
@click.option(
    "--open_cross_domain", type=click.Choice(["true", "false"]), help="是否开启跨域"
)
@click.option("--default_bind_host", help="默认绑定host")
@click.option("--webui_server_port", type=int, help="webui服务端口")
@click.option("--api_server_port", type=int, help="api服务端口")
@click.option("--clear", is_flag=True, help="清除配置")
@click.option("--show", is_flag=True, help="显示配置")
def server(**kwargs):
    if kwargs["httpx_default_timeout"]:
        config_server_workspace.set_httpx_default_timeout(
            httpx_default_timeout=kwargs["httpx_default_timeout"]
        )
    if kwargs["open_cross_domain"]:
        if kwargs["open_cross_domain"].lower() == "true":
            config_server_workspace.set_open_cross_domain(True)
        else:
            config_server_workspace.set_open_cross_domain(False)
    if kwargs["default_bind_host"]:
        config_server_workspace.set_default_bind_host(
            default_bind_host=kwargs["default_bind_host"]
        )

    if kwargs["webui_server_port"]:
        config_server_workspace.set_webui_server_port(
            webui_server_port=kwargs["webui_server_port"]
        )

    if kwargs["api_server_port"]:
        config_server_workspace.set_api_server_port(
            api_server_port=kwargs["api_server_port"]
        )

    if kwargs["clear"]:
        config_server_workspace.clear()
    if kwargs["show"]:
        print(config_server_workspace.get_config())


@main.command("kb", help="知识库配置")
@click.option("--set_default_knowledge_base", help="设置默认知识库")
@click.option("--set_default_vs_type", help="设置默认vs类型")
@click.option("--set_cached_vs_num", type=int, help="设置缓存vs数量")
@click.option("--set_cached_memo_vs_num", type=int, help="设置缓存memo vs数量")
@click.option("--set_chunk_size", type=int, help="设置chunk大小")
@click.option("--set_overlap_size", type=int, help="设置overlap大小")
@click.option("--set_vector_search_top_k", type=int, help="设置vector search top k")
@click.option("--set_score_threshold", type=float, help="设置score阈值")
@click.option("--set_default_search_engine", help="设置默认搜索引擎")
@click.option("--set_search_engine_top_k", type=int, help="设置搜索引擎top k")
@click.option(
    "--set_zh_title_enhance",
    type=click.Choice(["true", "false"]),
    help="是否开启中文标题增强",
)
@click.option("--pdf-ocr-threshold", type=(float, float), help="pdf ocr threshold")
@click.option(
    "--set_kb_info",
    type=str,
    help="""每个知识库的初始化介绍，用于在初始化知识库时显示和Agent调用，
                                                            没写则没有介绍，不会被Agent调用。 
                                                            as a JSON string.
                                                            Example:  "{\"samples\": \"关于本项目issue的解答\"}"
                                                            """,
)
@click.option("--set_kb_root_path", help="设置知识库根路径")
@click.option("--set_db_root_path", help="设置db根路径")
@click.option("--set_sqlalchemy_database_uri", help="设置sqlalchemy数据库uri")
@click.option("--set_text_splitter_name", help="设置text splitter名称")
@click.option("--set_embedding_keyword_file", help="设置embedding关键词文件")
@click.option("--clear", is_flag=True, help="清除配置")
@click.option("--show", is_flag=True, help="显示配置")
def kb(**kwargs):
    if kwargs["set_default_knowledge_base"]:
        config_kb_workspace.set_default_knowledge_base(
            default_knowledge_base=kwargs["set_default_knowledge_base"]
        )
    if kwargs["set_default_vs_type"]:
        config_kb_workspace.set_default_vs_type(
            default_vs_type=kwargs["set_default_vs_type"]
        )
    if kwargs["set_cached_vs_num"]:
        config_kb_workspace.set_cached_vs_num(cached_vs_num=kwargs["set_cached_vs_num"])
    if kwargs["set_cached_memo_vs_num"]:
        config_kb_workspace.set_cached_memo_vs_num(
            cached_memo_vs_num=kwargs["set_cached_memo_vs_num"]
        )
    if kwargs["set_chunk_size"]:
        config_kb_workspace.set_chunk_size(chunk_size=kwargs["set_chunk_size"])
    if kwargs["set_overlap_size"]:
        config_kb_workspace.set_overlap_size(overlap_size=kwargs["set_overlap_size"])
    if kwargs["set_vector_search_top_k"]:
        config_kb_workspace.set_vector_search_top_k(
            vector_search_top_k=kwargs["set_vector_search_top_k"]
        )
    if kwargs["set_score_threshold"]:
        config_kb_workspace.set_score_threshold(
            score_threshold=kwargs["set_score_threshold"]
        )
    if kwargs["set_default_search_engine"]:
        config_kb_workspace.set_default_search_engine(
            default_search_engine=kwargs["set_default_search_engine"]
        )
    if kwargs["set_search_engine_top_k"]:
        config_model_workspace.set_search_engine_top_k(
            search_engine_top_k=kwargs["set_search_engine_top_k"]
        )
    if kwargs["set_zh_title_enhance"]:
        if kwargs["set_zh_title_enhance"].lower() == "true":
            config_kb_workspace.set_zh_title_enhance(True)
        else:
            config_kb_workspace.set_zh_title_enhance(False)
    if kwargs["pdf_ocr_threshold"]:
        config_kb_workspace.set_pdf_ocr_threshold(
            pdf_ocr_threshold=kwargs["pdf_ocr_threshold"]
        )
    if kwargs["set_kb_info"]:
        kb_info_dict = json.loads(kwargs["set_kb_info"])
        config_kb_workspace.set_kb_info(kb_info=kb_info_dict)
    if kwargs["set_kb_root_path"]:
        config_kb_workspace.set_kb_root_path(kb_root_path=kwargs["set_kb_root_path"])
    if kwargs["set_db_root_path"]:
        config_kb_workspace.set_db_root_path(db_root_path=kwargs["set_db_root_path"])
    if kwargs["set_sqlalchemy_database_uri"]:
        config_kb_workspace.set_sqlalchemy_database_uri(
            sqlalchemy_database_uri=kwargs["set_sqlalchemy_database_uri"]
        )
    if kwargs["set_text_splitter_name"]:
        config_kb_workspace.set_text_splitter_name(
            text_splitter_name=kwargs["set_text_splitter_name"]
        )
    if kwargs["set_embedding_keyword_file"]:
        config_kb_workspace.set_embedding_keyword_file(
            embedding_keyword_file=kwargs["set_embedding_keyword_file"]
        )

    if kwargs["clear"]:
        config_kb_workspace.clear()
    if kwargs["show"]:
        print(config_kb_workspace.get_config())


if __name__ == "__main__":
    main()

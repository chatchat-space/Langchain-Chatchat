import click
from pathlib import Path
import shutil
import typing as t

from chatchat.startup import main as startup_main
from chatchat.init_database import main as kb_main, create_tables, folder2db
from chatchat.settings import Settings
from chatchat.utils import build_logger
from chatchat.server.utils import get_default_embedding


logger = build_logger()


@click.group(help="chatchat 命令行工具")
def main():
    ...


@main.command("init", help="项目初始化")
@click.option("-x", "--xinference-endpoint", "xf_endpoint",
              help="指定Xinference API 服务地址。默认为 http://127.0.0.1:9997/v1")
@click.option("-l", "--llm-model",
              help="指定默认 LLM 模型。默认为 glm4-chat")
@click.option("-e", "--embed-model",
              help="指定默认 Embedding 模型。默认为 bge-large-zh-v1.5")
@click.option("-r", "--recreate-kb",
              is_flag=True,
              show_default=True,
              default=False,
              help="同时重建知识库（必须确保指定的 embed model 可用）。")
@click.option("-k", "--kb-names", "kb_names",
              show_default=True,
              default="samples",
              help="要重建知识库的名称。可以指定多个知识库名称，以 , 分隔。")
def init(
    xf_endpoint: str = "",
    llm_model: str = "",
    embed_model: str = "",
    recreate_kb: bool = False,
    kb_names: str = "",
):
    Settings.set_auto_reload(False)
    bs = Settings.basic_settings
    kb_names = [x.strip() for x in kb_names.split(",")]
    logger.success(f"开始初始化项目数据目录：{Settings.CHATCHAT_ROOT}")
    Settings.basic_settings.make_dirs()
    logger.success("创建所有数据目录：成功。")
    if(bs.PACKAGE_ROOT / "data/knowledge_base/samples" != Path(bs.KB_ROOT_PATH) / "samples"):
        shutil.copytree(bs.PACKAGE_ROOT / "data/knowledge_base/samples", Path(bs.KB_ROOT_PATH) / "samples", dirs_exist_ok=True)
    logger.success("复制 samples 知识库文件：成功。")
    create_tables()
    logger.success("初始化知识库数据库：成功。")

    if xf_endpoint:
        Settings.model_settings.MODEL_PLATFORMS[0].api_base_url = xf_endpoint
    if llm_model:
        Settings.model_settings.DEFAULT_LLM_MODEL = llm_model
    if embed_model:
        Settings.model_settings.DEFAULT_EMBEDDING_MODEL = embed_model

    Settings.createl_all_templates()
    Settings.set_auto_reload(True)

    logger.success("生成默认配置文件：成功。")
    logger.success("请先检查确认 model_settings.yaml 里模型平台、LLM模型和Embed模型信息已经正确")

    if recreate_kb:
        folder2db(kb_names=kb_names,
                  mode="recreate_vs",
                  vs_type=Settings.kb_settings.DEFAULT_VS_TYPE,
                  embed_model=get_default_embedding())
        logger.success("<green>所有初始化已完成，执行 chatchat start -a 启动服务。</green>")
    else:
        logger.success("执行 chatchat kb -r 初始化知识库，然后 chatchat start -a 启动服务。")


main.add_command(startup_main, "start")
main.add_command(kb_main, "kb")


if __name__ == "__main__":
    main()

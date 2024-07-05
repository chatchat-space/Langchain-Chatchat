import click
from pathlib import Path
import shutil
import typing as t

from chatchat.startup import main as startup_main
from chatchat.init_database import main as kb_main, create_tables
from chatchat.settings import Settings
from chatchat.utils import build_logger


logger = build_logger()


@click.group(help="chatchat 命令行工具")
def main():
    ...


@main.command("init", help="项目初始化")
# @click.option("-k", "--recreate-kb", "kb_names",
#               show_default=True,
#               default="samples",
#               help="同时重建知识库。可以指定多个知识库名称，以 , 分隔。")
def init():
    bs = Settings.basic_settings
    logger.info(f"开始初始化项目数据目录：{Settings.CHATCHAT_ROOT}")
    Settings.basic_settings.make_dirs()
    logger.info("创建所有数据目录：成功。")
    shutil.copytree(bs.PACKAGE_ROOT / "data/knowledge_base/samples", Path(bs.KB_ROOT_PATH) / "samples", dirs_exist_ok=True)
    logger.info("复制 samples 知识库：成功。")
    Settings.createl_all_templates()
    logger.info("生成默认配置文件：成功。")
    logger.warning("<red>请先修改 model_settings.yaml 配置正确的模型平台、LLM模型和Embed模型，然后执行 chatchat kb -r 初始化知识库。</red>")


main.add_command(startup_main, "start")
main.add_command(kb_main, "kb")


if __name__ == "__main__":
    main()

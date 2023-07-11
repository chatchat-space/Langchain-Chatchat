import click

from api import api_start as api_start
from cli_demo import main as cli_start
from configs.model_config import llm_model_dict, embedding_model_dict


@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    pass


@cli.group()
def llm():
    pass


@llm.command(name="ls")
def llm_ls():
    for k in llm_model_dict.keys():
        print(k)


@cli.group()
def embedding():
    pass


@embedding.command(name="ls")
def embedding_ls():
    for k in embedding_model_dict.keys():
        print(k)


@cli.group()
def start():
    pass


@start.command(name="api", context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--ip', default='0.0.0.0', show_default=True, type=str, help='api_server listen address.')
@click.option('-p', '--port', default=7861, show_default=True, type=int, help='api_server listen port.')
@click.option('-k', '--ssl_keyfile', type=int, help='enable api https/wss service, specify the ssl keyfile path.')
@click.option('-c', '--ssl_certfile', type=int, help='enable api https/wss service, specify the ssl certificate file path.')
def start_api(ip, port, **kwargs):
    # 调用api_start之前需要先loadCheckPoint,并传入加载检查点的参数，
    # 理论上可以用click包进行包装，但过于繁琐，改动较大，
    # 此处仍用parser包，并以models.loader.args.DEFAULT_ARGS的参数为默认参数
    # 如有改动需要可以更改models.loader.args.DEFAULT_ARGS
    from models import shared
    from models.loader import LoaderCheckPoint
    from models.loader.args import DEFAULT_ARGS
    shared.loaderCheckPoint = LoaderCheckPoint(DEFAULT_ARGS)
    api_start(host=ip, port=port, **kwargs)

#     # 通过cli.py调用cli_demo时需要在cli.py里初始化模型，否则会报错：
    # langchain-ChatGLM: error: unrecognized arguments: start cli
    # 为此需要先将
    # args = None
    # args = parser.parse_args()
    # args_dict = vars(args)
    # shared.loaderCheckPoint = LoaderCheckPoint(args_dict)
    # 语句从main函数里取出放到函数外部
    # 然后在cli.py里初始化

@start.command(name="cli", context_settings=dict(help_option_names=['-h', '--help']))
def start_cli():
    print("通过cli.py调用cli_demo...")

    from models import shared
    from models.loader import LoaderCheckPoint
    from models.loader.args import DEFAULT_ARGS
    shared.loaderCheckPoint = LoaderCheckPoint(DEFAULT_ARGS)
    cli_start()
    
# 同cli命令，通过cli.py调用webui时，argparse的初始化需要放到cli.py里，
# 但由于webui.py里，模型初始化通过init_model函数实现，也无法简单地分离出主函数,
# 因此除非对webui进行大改，否则无法通过python cli.py start webui 调用webui。
# 故建议不要通过以上命令启动webui,将下述语句注释掉

@start.command(name="webui", context_settings=dict(help_option_names=['-h', '--help']))
def start_webui():
    import webui


cli()

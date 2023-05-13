import click

from api import api_start as api_start
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
def start_api(ip, port):
    api_start(host=ip, port=port)


@start.command(name="cli", context_settings=dict(help_option_names=['-h', '--help']))
def start_cli():
    import cli_demo
    cli_demo.main()


@start.command(name="webui", context_settings=dict(help_option_names=['-h', '--help']))
def start_webui():
    import webui


cli()

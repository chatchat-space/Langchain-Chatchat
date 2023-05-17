import click

from api import api_start as api_start
from configs.model_config import llm_model_dict, embedding_model_dict
from core.config import ConfigWarp


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
@click.option('-i', '--ip', show_default=True, type=str, help='api_server listen address.')
@click.option('-p', '--port', show_default=True, type=int, help='api_server listen port.')
@click.option('-c', '--config', default='api_config', show_default=True, type=str, help='use config name ignore .yaml')
def start_api(ip, port, config):
    overrides = []
    if ip is not None:
        overrides.append('api_server.host=' + ip)
    if port is not None:
        overrides.append('api_server.host=' + port)
    cfg = ConfigWarp(config, overrides=overrides)
    api_start(cfg)


@start.command(name="cli", context_settings=dict(help_option_names=['-h', '--help']))
def start_cli():
    import cli_demo
    cli_demo.main()


@start.command(name="webui", context_settings=dict(help_option_names=['-h', '--help']))
def start_webui():
    import webui


cli()

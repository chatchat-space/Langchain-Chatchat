from chatchat.configs import (
    config_basic_workspace,
    config_model_workspace,
)

# We cannot lazy-load click here because its used via decorators.
import click


@click.group(help="指令` chatchat-config` 工作空间配置")
def main():
    pass


@main.command("basic", help="基础配置")
@click.option("--verbose", type=click.Choice(["true", "false"]), help="是否开启详细日志")
@click.option("--data", help="数据存放路径")
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
@click.option("--model_providers_cfg_path_config", help="模型平台配置文件路径")
@click.option("--model_providers_cfg_host", help="模型平台配置服务host")
@click.option("--model_providers_cfg_port", type=int, help="模型平台配置服务port")
@click.option("--clear", is_flag=True, help="清除配置")
@click.option("--show", is_flag=True, help="显示配置")
def model(**kwargs):

    if kwargs["default_llm_model"]:
        config_model_workspace.set_default_llm_model(llm_model=kwargs["default_llm_model"])
    if kwargs["default_embedding_model"]:
        config_model_workspace.set_default_embedding_model(embedding_model=kwargs["default_embedding_model"])

    if kwargs["agent_model"]:
        config_model_workspace.set_agent_model(agent_model=kwargs["agent_model"])

    if kwargs["history_len"]:
        config_model_workspace.set_history_len(history_len=kwargs["history_len"])

    if kwargs["max_tokens"]:
        config_model_workspace.set_max_tokens(max_tokens=kwargs["max_tokens"])

    if kwargs["temperature"]:
        config_model_workspace.set_temperature(temperature=kwargs["temperature"])

    if kwargs["support_agent_models"]:
        config_model_workspace.set_support_agent_models(support_agent_models=kwargs["support_agent_models"])

    if kwargs["model_providers_cfg_path_config"]:
        config_model_workspace.set_model_providers_cfg_path_config(model_providers_cfg_path_config=kwargs["model_providers_cfg_path_config"])

    if kwargs["model_providers_cfg_host"]:
        config_model_workspace.set_model_providers_cfg_host(model_providers_cfg_host=kwargs["model_providers_cfg_host"])

    if kwargs["model_providers_cfg_port"]:
        config_model_workspace.set_model_providers_cfg_port(model_providers_cfg_port=kwargs["model_providers_cfg_port"])

    if kwargs["clear"]:
        config_model_workspace.clear()
    if kwargs["show"]:
        print(config_model_workspace.get_config())


if __name__ == "__main__":
    main()

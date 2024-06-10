from chatchat.configs import config_basic_workspace as workspace


def main():
    import argparse

    parser = argparse.ArgumentParser(description="指令` chatchat-config` 工作空间配置")
    # 只能选择true或false
    parser.add_argument(
        "-v",
        "--verbose",
        choices=["true", "false"],
        help="是否开启详细日志"
    )
    parser.add_argument(
        "-d",
        "--data",
        help="数据存放路径"
    )
    parser.add_argument(
        "-f",
        "--format",
        help="日志格式"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="清除配置"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="显示配置"
    )
    args = parser.parse_args()

    if args.verbose:
        if args.verbose.lower() == "true":
            workspace.set_log_verbose(True)
        else:
            workspace.set_log_verbose(False)
    if args.data:
        workspace.set_data_path(args.data)
    if args.format:
        workspace.set_log_format(args.format)
    if args.clear:
        workspace.clear()
    if args.show:
        print(workspace.get_config())


if __name__ == "__main__":
    main()

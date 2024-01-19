import logging
import sys
import os
import subprocess
import threading
import re
import locale

logger = logging.getLogger(__name__)
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
processed_install = set()
pip_list = None


def handle_stream(stream, prefix):
    stream.reconfigure(encoding=locale.getpreferredencoding(), errors='replace')
    for msg in stream:
        if prefix == '[!]' and ('it/s]' in msg or 's/it]' in msg) and ('%|' in msg or 'it [' in msg):
            if msg.startswith('100%'):
                print('\r' + msg, end="", file=sys.stderr),
            else:
                print('\r' + msg[:-1], end="", file=sys.stderr),
        else:
            if prefix == '[!]':
                print(prefix, msg, end="", file=sys.stderr)
            else:
                print(prefix, msg, end="")


def get_installed_packages():
    global pip_list

    if pip_list is None:
        try:
            result = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], universal_newlines=True)
            pip_list = set([line.split()[0].lower() for line in result.split('\n') if line.strip()])
        except subprocess.CalledProcessError as e:
            print(f"[ComfyUI-Manager] Failed to retrieve the information of installed pip packages.")
            return set()

    return pip_list


def is_installed(name):
    name = name.strip()

    if name.startswith('#'):
        return True

    pattern = r'([^<>!=]+)([<>!=]=?)'
    match = re.search(pattern, name)

    if match:
        name = match.group(1)

    return name.lower() in get_installed_packages()


def process_wrap(cmd_str, cwd_path, handler=None):
    process = subprocess.Popen(cmd_str, cwd=cwd_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               bufsize=1)

    if handler is None:
        handler = handle_stream

    stdout_thread = threading.Thread(target=handler, args=(process.stdout, ""))
    stderr_thread = threading.Thread(target=handler, args=(process.stderr, "[!]"))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    return process.wait()


def install():
    try:
        requirements_path = os.path.join(root_dir, 'requirements.txt')

        this_exit_code = 0

        if os.path.exists(requirements_path):
            with open(requirements_path, 'r', encoding="UTF-8") as file:
                for line in file:
                    package_name = line.strip()
                    if package_name and not is_installed(package_name):
                        install_cmd = [sys.executable, "-m", "pip", "install", package_name]
                        this_exit_code += process_wrap(install_cmd, root_dir)

        if this_exit_code != 0:
            logger.info(f"[openai_plugins]  Restoring fastchat  is failed.")

    except Exception as e:
        logger.error(f"[openai_plugins] Restoring fastchat is failed.", exc_info=True)


if __name__ == "__main__":
    install()

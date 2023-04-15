import os
import subprocess
import re

def get_latest_tag():
    output = subprocess.check_output(['git', 'tag'])
    tags = output.decode('utf-8').split('\n')[:-1]
    latest_tag = sorted(tags, key=lambda t: tuple(map(int, re.match(r'v(\d+)\.(\d+)\.(\d+)', t).groups())))[-1]
    return latest_tag

def update_version_number(latest_tag, increment):
    major, minor, patch = map(int, re.match(r'v(\d+)\.(\d+)\.(\d+)', latest_tag).groups())
    if increment == 'X':
        major += 1
        minor, patch = 0, 0
    elif increment == 'Y':
        minor += 1
        patch = 0
    elif increment == 'Z':
        patch += 1
    new_version = f"v{major}.{minor}.{patch}"
    return new_version

def main():
    print("当前最近的Git标签：")
    latest_tag = get_latest_tag()
    print(latest_tag)

    print("请选择要递增的版本号部分（X, Y, Z）：")
    increment = input().upper()

    while increment not in ['X', 'Y', 'Z']:
        print("输入错误，请输入X, Y或Z：")
        increment = input().upper()

    new_version = update_version_number(latest_tag, increment)
    print(f"新的版本号为：{new_version}")

    print("确认更新版本号并推送到远程仓库？（y/n）")
    confirmation = input().lower()

    if confirmation == 'y':
        subprocess.run(['git', 'tag', new_version])
        subprocess.run(['git', 'push', 'origin', new_version])
        print("新版本号已创建并推送到远程仓库。")
    else:
        print("操作已取消。")

if __name__ == '__main__':
    main()

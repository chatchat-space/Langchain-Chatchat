# mac设备上的grep命令可能不支持grep -P选项，请使用Homebrew安装;或使用ggrep命令
if [[ "$(uname)" == "Darwin" ]]; then
    ps -eo pid,user,command|grep -P 'server/api.py|webui.py|fastchat.serve|multiprocessing'|grep -v grep|awk '{print $1}'|xargs kill -9
else
    ps -eo pid,user,cmd|grep -P 'server/api.py|webui.py|fastchat.serve|multiprocessing'|grep -v grep|awk '{print $1}'|xargs kill -9
fi
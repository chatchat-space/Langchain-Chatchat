#基于的基础镜像
FROM python:3.11.7
#代码添加当前目录所有内容到code文件夹
ADD . /code
# 设置code文件夹是工作目录
WORKDIR /code
# 安装支持
RUN pip install -r requirements.txt && python init_database.py --recreate-vs
CMD [ "python","startup.py -a"]
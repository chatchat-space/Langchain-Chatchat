### chatchat 容器化部署指引

> 提示: 此指引为在 Linux 环境下编写完成, 其他环境下暂未测试, 理论上可行.
> 
> Langchain-Chatchat docker 镜像已支持多架构, 欢迎大家自行测试.

#### 一. Langchain-Chatchat 体验部署

##### 1. 安装 docker-compose
寻找适合你环境的 docker-compose 版本, 请参考 [Docker-Compose](https://github.com/docker/compose).

举例: Linux X86 环境 可下载 [docker-compose-linux-x86_64](https://github.com/docker/compose/releases/download/v2.27.3/docker-compose-linux-x86_64) 使用.
```shell
cd ~
wget https://github.com/docker/compose/releases/download/v2.27.3/docker-compose-linux-x86_64
mv docker-compose-linux-x86_64 /usr/bin/docker-compose
which docker-compose
```
/usr/bin/docker-compose
```shell
docker-compose -v
```
Docker Compose version v2.27.3

##### 2. 安装 NVIDIA Container Toolkit
寻找适合你环境的 NVIDIA Container Toolkit 版本, 请参考: [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

安装完成后记得按照刚刚文档中`Configuring Docker`章节对 docker 进行初始化. 

##### 3. 创建 xinference 数据缓存路径

这一步强烈建议, 因为可以将 xinference 缓存的模型都保存到本地, 长期使用. 
```shell
mkdir -p ~/xinference
```

##### 4. 下载 chatchat & xinference 启动配置文件(docker-compose.yaml)
```shell
cd ~
wget https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docker/docker-compose.yaml
```

##### 5. 启动 chatchat & xinference 服务
```shell
docker-compose up -d
```
出现如下日志即为成功 ( 第一次启动需要下载 docker 镜像, 时间较长, 这里已经提前下载好了 )
```text
WARN[0000] /root/docker-compose.yaml: `version` is obsolete 
[+] Running 2/2
 ✔ Container root-chatchat-1    Started                                                                                             0.2s 
 ✔ Container root-xinference-1  Started                                                                                             0.3s
```

##### 6.检查服务启动情况
```shell
docker-compose up -d
```
```text
WARN[0000] /root/docker-compose.yaml: `version` is obsolete 
NAME                IMAGE                           COMMAND                  SERVICE      CREATED         STATUS         PORTS
root-chatchat-1     chatimage/chatchat:0.3.1.2-2024-0720   "chatchat -a"            chatchat     3 minutes ago   Up 3 minutes   
root-xinference-1   xprobe/xinference:v0.12.1       "/opt/nvidia/nvidia_…"   xinference   3 minutes ago   Up 3 minutes
```
```shell
ss -anptl | grep -E '(8501|7861|9997)'
```
```text
LISTEN 0      128          0.0.0.0:9997       0.0.0.0:*    users:(("pt_main_thread",pid=1489804,fd=21))
LISTEN 0      128          0.0.0.0:8501       0.0.0.0:*    users:(("python",pid=1490078,fd=10))        
LISTEN 0      128          0.0.0.0:7861       0.0.0.0:*    users:(("python",pid=1490014,fd=9))
```
如上, 服务均已正常启动, 即可体验使用.

> 提示: 先登陆 xinference ui `http://<your_ip>:9997` 启动 llm 和 embedding 后, 再登陆 chatchat ui `http://<your_ip>:8501` 进行体验.
> 
> 详细文档:
> - Langchain-chatchat 使用请参考: [LangChain-Chatchat](/README.md)
> 
> - Xinference 使用请参考: [欢迎来到 Xinference！](https://inference.readthedocs.io/zh-cn/latest/index.html)

#### 二. Langchain-Chatchat 进阶部署

##### 1. 按照 `Langchain-Chatchat 体验部署` 内容顺序依次完成

##### 2. 创建 chatchat 数据缓存路径
```shell
cd ~
mkdir -p ~/chatchat
```

##### 3. 修改 `docker-compose.yaml` 文件内容

原文件内容:
```yaml
  (上文 ...)
  chatchat:
    image: chatimage/chatchat:0.3.1.2-2024-0720
    (省略 ...)
    # 将本地路径(~/chatchat/data)挂载到容器默认数据路径(/usr/local/lib/python3.11/site-packages/chatchat/data)中
    # volumes:
    #   - ~/chatchat/data:/usr/local/lib/python3.11/site-packages/chatchat/data
  (下文 ...)
```
将 `volumes` 字段注释打开, 并按照 `YAML` 格式对齐, 如下:
```yaml
  (上文 ...)
  chatchat:
    image: chatimage/chatchat:0.3.1.2-2024-0720
    (省略 ...)
    # 将本地路径(~/chatchat/data)挂载到容器默认数据路径(/usr/local/lib/python3.11/site-packages/chatchat/data)中
    volumes:
      - ~/chatchat/data:/usr/local/lib/python3.11/site-packages/chatchat/data
  (下文 ...)
```

##### 4. 下载数据库初始文件

> 提示: 这里的 `data.tar.gz` 文件仅包含初始化后的数据库 `samples` 文件一份及相应目录结构, 用户可将原先数据和目录结构迁移此处.
> > [!WARNING] 请您先备份好您的数据再进行迁移!!!

```shell
cd ~/chatchat
wget https://github.com/chatchat-space/Langchain-Chatchat/blob/master/docker/data.tar.gz
tar -xvf data.tar.gz
```
```shell
cd data
pwd
```
/root/chatchat/data
```shell
ls -l
```
```text
total 20
drwxr-xr-x  3 root root 4096 Jun 22 10:46 knowledge_base
drwxr-xr-x 18 root root 4096 Jun 22 10:52 logs
drwxr-xr-x  5 root root 4096 Jun 22 10:46 media
drwxr-xr-x  5 root root 4096 Jun 22 10:46 nltk_data
drwxr-xr-x  3 root root 4096 Jun 22 10:46 temp
```
 
##### 6. 重启 chatchat 服务

这一步需要到 `docker-compose.yaml` 文件所在路径下执行, 即:
```shell
cd ~
docker-compose down chatchat
docker-compose up -d chatchat
```
操作及检查结果如下:
```text
[root@VM-2-15-centos ~]# docker-compose down chatchat
WARN[0000] /root/docker-compose.yaml: `version` is obsolete 
[+] Running 1/1
 ✔ Container root-chatchat-1  Removed                                                                                               0.5s 
[root@VM-2-15-centos ~]# docker-compose up -d
WARN[0000] /root/docker-compose.yaml: `version` is obsolete 
[+] Running 2/2
 ✔ Container root-xinference-1  Running                                                                                             0.0s 
 ✔ Container root-chatchat-1    Started                                                                                             0.2s
[root@VM-2-15-centos ~]# docker-compose ps
WARN[0000] /root/docker-compose.yaml: `version` is obsolete 
NAME                IMAGE                           COMMAND                  SERVICE      CREATED          STATUS          PORTS
root-chatchat-1     chatimage/chatchat:0.3.1.2-2024-0720   "chatchat -a"            chatchat     33 seconds ago   Up 32 seconds   
root-xinference-1   xprobe/xinference:v0.12.1       "/opt/nvidia/nvidia_…"   xinference   45 minutes ago   Up 45 minutes   
[root@VM-2-15-centos ~]# ss -anptl | grep -E '(8501|7861|9997)'
LISTEN 0      128          0.0.0.0:9997       0.0.0.0:*    users:(("pt_main_thread",pid=1489804,fd=21))
LISTEN 0      128          0.0.0.0:8501       0.0.0.0:*    users:(("python",pid=1515944,fd=10))        
LISTEN 0      128          0.0.0.0:7861       0.0.0.0:*    users:(("python",pid=1515878,fd=9))
```

# 创建代码根目录
mkdir /home/langchain

## 切换代码根目录
cd /home/langchain

## 拉取仓库代码
git clone https://github.com/chatchat-space/Langchain-Chatchat.git .

## 切换Configs文件夹，复制所有的配置档并去除文档后缀.example
/home/langchain/configs/

## 配置key
/home/langchain/configs/model_config.py

## 切换代码根目录
cd /home/langchain

## 制作镜像（自行修改镜像名称与版本号）
docker build -t {image_name}:{image_tag} .

## 修改YAML里的镜像名称与版本号
langchain_sample.yaml

## 创建K8S资源
kubectl apply -f langchain_sample.yaml

## 删除K8S资源
kubectl delete -f langchain_sample.yaml

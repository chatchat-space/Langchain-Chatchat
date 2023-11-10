
# 实现基于ES的数据插入、检索、删除、更新
```shell
author: 唐国梁Tommy
e-mail: flytang186@qq.com

如果遇到任何问题，可以与我联系，我这边部署后服务是没有问题的。
```

## 第1步：ES docker部署
```shell
docker network create elastic
docker run -id --name elasticsearch --net elastic -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "xpack.security.http.ssl.enabled=false" -t docker.elastic.co/elasticsearch/elasticsearch:8.8.2
```

### 第2步：Kibana docker部署
**注意：Kibana版本与ES保持一致**
```shell
docker pull docker.elastic.co/kibana/kibana:{version} 
docker run --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:{version}
```

### 第3步：核心代码
```shell
1. 核心代码路径
server/knowledge_base/kb_service/es_kb_service.py

2. 需要在 configs/model_config.py 中 配置 ES参数（IP， PORT）等；
```
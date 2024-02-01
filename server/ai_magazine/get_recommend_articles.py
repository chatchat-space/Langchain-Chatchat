from fastapi import Body
from fastapi.responses import JSONResponse
from elasticsearch import Elasticsearch
from typing import *
import re
import time

RETURNED_ARTICLE_NUM = 10


def get_article_res(article):
    res = {
        "contentUUID": article["_source"]["contentUUID"],
        "title": article["_source"]["title"],
        "article": article["_source"]["contentUrl"],
        "relation": {
            "link": "",
            "title": article["_source"]["title"],
            "introduction": article["_source"]["description"],
        },
    }
    return res


def get_article_quality_check(major, articles):
    # 如果文章数量不够, 记录日志
    if len(articles) < RETURNED_ARTICLE_NUM:
        with open("server/ai_magazine/推荐记录.txt", "a") as f:
            check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write(check_time + " " + major + "文章数量不足\n")


# 连接ES
es = Elasticsearch(
    ["http://localhost:9200"],
    sniff_on_start=False,  # 连接前测试
    sniff_on_connection_fail=True,  # 节点无响应时刷新节点
    sniffer_timeout=60,  # 设置超时时间
)


def get_recommend_articles(
    collegeTags: Dict = Body(
        {},
        description="院校相关标签",
        examples=[
            {
                "意向学校": ["清华大学"],
                "推荐学校": {"冲刺学校": ["北京大学"], "稳妥学校": ["中国人民大学"], "保底学校": ["北京师范大学"]},
            }
        ],
    ),
    majorTags: Dict = Body(
        {},
        description="院校相关标签",
        examples=[
            {
                "意向专业": ["计算机科学与技术"],
            }
        ],
    ),
    usedUUIDs: List = Body(
        [],
        description="已经使用过的文章UUID",
        examples=[
            ["0b6df52aa3d811eea4737af451f953bb", "0a6ebca4a3d811eea4737af451f953bb"]
        ],
    ),
):
    """
    a

    Args:
        collegeTags (_type_, optional): _description_. Defaults to Body({}, description="院校相关标签", examples=[ { "意向学校":["清华大学"], "推荐学校": { "冲刺学校":["北京大学"], "稳妥学校":["中国人民大学"], "保底学校":["北京师范大学"] } }] ).
        majorTags (_type_, optional): _description_. Defaults to Body({}, description="院校相关标签", examples=[ { "意向专业":["计算机科学与技术"], }] ).
        usedUUIDs (List, optional): _description_. Defaults to Body([], description="已经使用过的文章UUID", examples=[["1234567890","12345678901"]]).

    Returns:
        _type_: _description_
    """

    print(collegeTags, majorTags, usedUUIDs)

    # 共有5个模块 1.专业探索 2.专业杰出人物 3. 专业前沿资讯 4.院校历史 5.院校招生政策
    # 1.专业探索, 查找所有relatedMajors和意向专业相同, 且topicTags为专业重点扫盲的文章
    major_explorer_articles = {}
    # 构建查询
    for major in majorTags["意向专业"]:
        major_explorer_articles = {"title": major + "重点扫盲", "children": []}
        print("意向专业", major)
        query = {
            "size": RETURNED_ARTICLE_NUM,  # 指定返回的文档数量
            "query": {
                "bool": {
                    "must": [
                        {"match": {"relatedMajors.name.keyword": major}},
                        {"match": {"topicTags.name.keyword": "专业重点扫盲"}},
                    ],
                    "must_not": [{"terms": {"contentUUID.keyword": usedUUIDs}}],
                }
            },
        }
        res = es.search(index="shijie", body=query)
        print("要排除的ids", usedUUIDs)
        get_article_quality_check(major, res["hits"]["hits"])
        for article in res["hits"]["hits"]:
            major_explorer_articles["children"].append(get_article_res(article))

    # 2.专业杰出如人物, 查找所有relatedMajors和意向专业相同, 且topicTags为专业杰出人物的文章
    major_outstanding_articles = {}
    # 构建查询
    for major in majorTags["意向专业"]:
        major_outstanding_articles = {"title": major + "杰出人物", "children": []}
        query = {
            "size": RETURNED_ARTICLE_NUM,  # 指定返回的文档数量
            "query": {
                "bool": {
                    "must": [
                        {"match": {"relatedMajors.name.keyword": major}},
                        {"match": {"topicTags.name.keyword": "专业杰出人物"}},
                    ],
                    "must_not": [{"terms": {"contentUUID.keyword": usedUUIDs}}],
                }
            },
        }
        res = es.search(index="shijie", body=query)
        get_article_quality_check(major, res["hits"]["hits"])
        for article in res["hits"]["hits"]:
            major_outstanding_articles["children"].append(get_article_res(article))
    # 3.专业前沿资讯, 查找所有relatedMajors和意向专业相同, 且topicTags为专业前沿资讯的文章
    major_frontier_articles = {}
    # 构建查询
    for major in majorTags["意向专业"]:
        major_frontier_articles = {"title": major + "前沿资讯", "children": []}
        query = {
            "size": RETURNED_ARTICLE_NUM,  # 指定返回的文档数量
            "query": {
                "bool": {
                    "must": [
                        {"match": {"relatedMajors.name.keyword": major}},
                        {"match": {"topicTags.name.keyword": "专业前沿资讯"}},
                    ],
                    "must_not": [{"terms": {"contentUUID.keyword": usedUUIDs}}],
                }
            },
        }
        res = es.search(index="shijie", body=query)
        get_article_quality_check(major, res["hits"]["hits"])
        for article in res["hits"]["hits"]:
            major_frontier_articles["children"].append(get_article_res(article))

    # 4.院校历史, 查找所有relatedUniversitie和意向学校相同, 且topicTags为院校历史的文章
    # 构建查询
    for university in collegeTags["意向学校"]:
        university_history_articles = {"title": university + "院校历史", "children": []}
        query = {
            "size": RETURNED_ARTICLE_NUM,  # 指定返回的文档数量
            "query": {
                "bool": {
                    "must": [
                        {"match": {"relatedUniversities.name.keyword": university}},
                        {"match": {"topicTags.name.keyword": "院校历史"}},
                    ],
                    "must_not": [{"terms": {"contentUUID.keyword": usedUUIDs}}],
                }
            },
        }
        res = es.search(index="shijie", body=query)
        get_article_quality_check(university, res["hits"]["hits"])
        for article in res["hits"]["hits"]:
            university_history_articles["children"].append(get_article_res(article))

    # 5.院校招生政策, 查找所有relatedUniversitie和意向学校相同, 且topicTags为院校招生政策的文章
    university_policy_articles = {}
    # 构建查询
    for university in collegeTags["意向学校"]:
        university_policy_articles = {"title": university + "院校政策", "children": []}
        query = {
            "size": RETURNED_ARTICLE_NUM,  # 指定返回的文档数量
            "query": {
                "bool": {
                    "must": [
                        {"match": {"relatedUniversities.name.keyword": university}},
                        {"match": {"topicTags.name.keyword": "院校政策"}},
                    ],
                    "must_not": [{"terms": {"contentUUID.keyword": usedUUIDs}}],
                }
            },
        }
        res = es.search(index="shijie", body=query)
        get_article_quality_check(university, res["hits"]["hits"])
        for article in res["hits"]["hits"]:
            university_policy_articles["children"].append(get_article_res(article))

    # 返回模版
    ret = {"interest_explore": []}
    ret["interest_explore"].extend(
        [
            major_explorer_articles,
            major_outstanding_articles,
            major_frontier_articles,
            university_history_articles,
            university_policy_articles,
        ]
    )

    return JSONResponse(ret)

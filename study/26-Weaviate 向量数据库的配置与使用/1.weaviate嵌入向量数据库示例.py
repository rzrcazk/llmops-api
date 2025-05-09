#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/29 22:36
@Author  : thezehui@gmail.com
@File    : 1.weaviate嵌入向量数据库示例.py
"""
import dotenv
import weaviate
import os
import ssl
import traceback
import requests

# 首先加载环境变量
dotenv.load_dotenv()

# 临时禁用SSL验证（仅用于开发环境，不建议在生产环境中使用）
ssl._create_default_https_context = ssl._create_unverified_context

# 检查并设置OpenAI API密钥
api_key = os.getenv('OPENAI_API_KEY', '')
if not api_key:
    print("警告: OPENAI_API_KEY 环境变量未设置或为空")
else:
    # 设置API密钥（虽然OpenAIEmbeddings会自动从环境变量获取，但为了明确起见）
    os.environ['OPENAI_API_KEY'] = api_key
    print(f"检测到API密钥: {api_key[:4]}{'*' * 16}")  # 只显示前4个字符，其余用*代替

# 测试OpenAI API连接
def test_openai_connection():
    """测试与OpenAI API的连接"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10,
            verify=False  # 禁用SSL验证，与上面的设置一致
        )
        if response.status_code == 200:
            print("OpenAI API连接测试成功")
            return True
        else:
            print(f"OpenAI API连接测试失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"OpenAI API连接测试异常: {e}")
        return False

# 导入需要的模块
from langchain_openai import OpenAIEmbeddings
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey
from weaviate.classes.query import Filter

# 1.原始文本数据与元数据
texts = [
    "笨笨是一只很喜欢睡觉的猫咪",
    "我喜欢在夜晚听音乐，这让我感到放松。",
    "猫咪在窗台上打盹，看起来非常可爱。",
    "学习新技能是每个人都应该追求的目标。",
    "我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
    "昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
    "我的手机突然关机了，让我有些焦虑。",
    "阅读是我每天都会做的事情，我觉得很充实。",
    "他们一起计划了一次周末的野餐，希望天气能好。",
    "我的狗喜欢追逐球，看起来非常开心。",
]
metadatas = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
    {"page": 6, "account_id": 1},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

# 测试OpenAI API连接
print("测试OpenAI API连接...")
api_connected = test_openai_connection()
if not api_connected:
    print("警告: OpenAI API连接测试失败，程序可能无法正常运行")
    print("建议检查网络连接、API密钥设置或使用代理")

# 2.创建连接客户端
try:
    print("连接Weaviate数据库...")
    client = weaviate.connect_to_local("10.10.1.8", 50080)
    print("Weaviate连接成功")
except Exception as e:
    print(f"连接Weaviate数据库失败: {e}")
    traceback.print_exc()
    exit(1)

# client = weaviate.connect_to_weaviate_cloud(
#     cluster_url="dne8v3ybteiqpkfqbh8kq.c0.asia-southeast1.gcp.weaviate.cloud",
#     auth_credentials=AuthApiKey("eVkcMClSL0fSyzyUP1FkS6PyHcnK9VJEGCTB"),
# )

try:
    print("初始化OpenAI Embeddings...")
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    print("OpenAI Embeddings初始化成功")
except Exception as e:
    print(f"初始化OpenAI Embeddings失败: {e}")
    traceback.print_exc()
    client.close()
    exit(1)

# 3.创建LangChain向量数据库实例
try:
    print("创建WeaviateVectorStore实例...")
    db = WeaviateVectorStore(
        client=client,
        index_name="Dataset",
        text_key="text",
        embedding=embedding,
    )
    print("WeaviateVectorStore实例创建成功")
except Exception as e:
    print(f"创建WeaviateVectorStore实例失败: {e}")
    traceback.print_exc()
    client.close()
    exit(1)

# 4.添加数据
try:
    print("开始添加文本数据...")
    ids = db.add_texts(texts, metadatas)
    print(f"成功添加文本，ID列表: {ids}")

    # 5.执行相似性搜索
    print("执行相似性搜索...")
    filters = Filter.by_property("page").greater_or_equal(5)
    results = db.similarity_search_with_score("笨笨", filters=filters)
    print(f"相似性搜索结果: {results}")
    
    print("作为检索器使用...")
    retriever = db.as_retriever()
    retrieval_results = retriever.invoke("笨笨")
    print(f"检索结果: {retrieval_results}")
except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
    print("详细错误堆栈:")
    traceback.print_exc()
    
    # 检查是否是OpenAI API相关错误
    if "openai" in str(e).lower():
        print("\nOpenAI API错误排查建议:")
        print("1. 确认OPENAI_API_KEY环境变量已正确设置")
        print("2. 检查API密钥是否有效且未过期")
        print("3. 检查网络连接和代理设置")
        print("4. 检查OpenAI服务是否可用")
        print("5. 如果在中国大陆网络环境，可能需要代理才能访问OpenAI API")
        print("6. 尝试使用官方提供的API代理，如api.openai-proxy.com")
finally:
    # 确保关闭连接
    print("关闭Weaviate客户端连接...")
    client.close()

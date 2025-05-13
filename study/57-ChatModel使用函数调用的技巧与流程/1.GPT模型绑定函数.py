#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/9 17:53
@Author  : thezehui@gmail.com
@File    : 1.GPT模型绑定函数.py
"""
import json
import os
from typing import type, Any, Type

import dotenv
import requests
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class GaodeWeatherArgsSchema(BaseModel):
    city: str = Field(description="需要查询天气预报的目标城市，例如：广州")


class GoogleSerperArgsSchema(BaseModel):
    query: str = Field(description="执行谷歌搜索的查询语句")


class GaodeWeatherTool(BaseTool):
    """查询天气的工具"""
    name: str = "gaode_weather"
    description: str = "查询指定城市的天气情况。使用此工具时，需要提供城市名称，如北京、上海"
    args_schema: type[GaodeWeatherArgsSchema] = GaodeWeatherArgsSchema

    def _run(self, city: str, *args: Any, **kwargs: Any) -> Any:
        """调用高德开放平台查询城市天气"""
        api_key = "你的高德API Key"
        # 省略实际API调用代码
        print(f"正在查询{city}的天气...")
        return f"{city}多云，气温18-26摄氏度，注意穿衣保暖。"


# 1.定义工具列表
gaode_weather = GaodeWeatherTool()
google_serper = GoogleSerperRun(
name: str = "google_serper",
    description=(
        "一个低成本的谷歌搜索API。"
        "当你需要回答有关时事的问题时，可以调用该工具。"
        "该工具的输入是搜索查询语句。"
    ),
args_schema: type = GoogleSerperArgsSchema,
    api_wrapper=GoogleSerperAPIWrapper(),
)
tool_dict = {
    gaode_weather.name: gaode_weather,
    google_serper.name: google_serper,
}
tools = [tool for tool in tool_dict.values()]

# 2.创建Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "你是由OpenAI开发的聊天机器人，可以帮助用户回答问题，必要时刻请调用工具帮助用户解答，如果问题需要多个工具回答，请一次性调用所有工具，不要分步调用"
    ),
    ("human", "{query}"),
])

# 3.创建大语言模型并绑定工具
llm = ChatOpenAI(model="gpt-4o")
llm_with_tool = llm.bind_tools(tools=tools)

# 4.创建链应用
chain = {"query": RunnablePassthrough()} | prompt | llm_with_tool

# 5.调用链应用，并获取输出响应
query = "上海现在天气怎样，并且请用谷歌搜索工具查询一下2024年巴黎奥运会中国代表团共获得几枚金牌？"
resp = chain.invoke(query)
tool_calls = resp.tool_calls

# 6.判断是工具调用还是正常输出结果
if len(tool_calls) <= 0:
    print("生成内容: ", resp.content)
else:
    # 7.将历史的系统消息、人类消息、AI消息组合
    messages = prompt.invoke(query).to_messages()
    messages.append(resp)

    # 8.循环遍历所有工具调用信息
    for tool_call in tool_calls:
        tool = tool_dict.get(tool_call.get("name"))  # 获取需要执行的工具
        print("正在执行工具: ", tool.name)
        content = tool.invoke(tool_call.get("args"))  # 工具执行的内容/结果
        print("工具返回结果: ", content)
        tool_call_id = tool_call.get("id")
        messages.append(ToolMessage(
            content=content,
            tool_call_id=tool_call_id,
        ))
    print("输出内容: ", llm.invoke(messages).content)

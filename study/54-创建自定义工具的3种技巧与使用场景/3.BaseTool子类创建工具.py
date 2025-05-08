#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/9 15:03
@Author  : 刘志祥
@File    : 3.BaseTool子类创建工具.py
"""
from typing import Any, Dict

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class MultiplyInput(BaseModel):
    a: float = Field(description="第一个数")
    b: float = Field(description="第二个数")


class MultiplyTool(BaseTool):
    """乘法计算工具"""
    name: str = "multiply"
    description: str = "当需要计算两个数相乘时使用此工具"
    args_schema: type = MultiplyInput

    def _run(self, a: float, b: float, **kwargs) -> float:
        """执行乘法计算"""
        return a * b


"""
# 测试代码
tool = MultiplyTool()
print(tool.name)
print(tool.description)
print(tool.args)
print(tool._run(3, 4))
print(tool._run(a=3, b=4))
"""

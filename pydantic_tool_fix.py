#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动修复 Pydantic v2 兼容性问题的脚本
"""
import os
import re
import sys

def fix_imports(file_path):
    """将 langchain_core.pydantic_v1 的导入改为 pydantic"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入语句
    patterns = [
        (r'from\s+langchain_core\.pydantic_v1\s+import\s+BaseModel,\s+Field', 'from pydantic import BaseModel, Field'),
        (r'from\s+langchain_core\.pydantic_v1\s+import\s+BaseModel', 'from pydantic import BaseModel'),
        (r'from\s+langchain_core\.pydantic_v1\s+import\s+Field', 'from pydantic import Field'),
        (r'from\s+langchain_core\.pydantic_v1\s+import\s+Field,\s+BaseModel', 'from pydantic import BaseModel, Field')
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # 检查是否进行了修改
    if content != open(file_path, 'r', encoding='utf-8').read():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已修复导入: {file_path}")
        return True
    return False

def fix_basetool_fields(file_path):
    """为 BaseTool 子类添加类型注解"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找 BaseTool 子类
    class_matches = re.findall(r'class\s+(\w+)\s*\(\s*BaseTool\s*\):', content)
    if not class_matches:
        return False
    
    # 检查并修复字段类型注解
    modified = False
    for class_name in class_matches:
        # 找到类定义区域
        class_pattern = re.compile(r'class\s+' + class_name + r'\s*\(\s*BaseTool\s*\):.*?(?=class|\Z)', re.DOTALL)
        class_match = class_pattern.search(content)
        if not class_match:
            continue
        
        class_content = class_match.group(0)
        original_class_content = class_content
        
        # 修复 name 字段
        name_pattern = re.compile(r'^\s*name\s*=\s*(["\'].*?["\'])', re.MULTILINE)
        name_match = name_pattern.search(class_content)
        if name_match and 'name:' not in name_match.group(0):
            class_content = name_pattern.sub(r'name: str = \1', class_content)
        
        # 修复 description 字段
        desc_pattern = re.compile(r'^\s*description\s*=\s*(["\'].*?["\'])', re.MULTILINE)
        desc_match = desc_pattern.search(class_content)
        if desc_match and 'description:' not in desc_match.group(0):
            class_content = desc_pattern.sub(r'description: str = \1', class_content)
        
        # 修复 args_schema 字段
        args_pattern = re.compile(r'^\s*args_schema\s*=\s*(\w+)', re.MULTILINE)
        args_match = args_pattern.search(class_content)
        if args_match and 'args_schema:' not in args_match.group(0):
            class_content = args_pattern.sub(r'args_schema: type = \1', class_content)
        
        # 如果有修改，更新内容
        if class_content != original_class_content:
            content = content.replace(original_class_content, class_content)
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已修复 BaseTool 子类字段: {file_path}")
        return True
    return False

def scan_directory(directory):
    """扫描目录并修复文件"""
    fixed_files = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports(file_path) or fix_basetool_fields(file_path):
                    fixed_files += 1
    return fixed_files

if __name__ == "__main__":
    target_dir = "." if len(sys.argv) < 2 else sys.argv[1]
    print(f"开始扫描目录: {target_dir}")
    fixed_count = scan_directory(target_dir)
    print(f"修复完成，共修复 {fixed_count} 个文件")
    print("请重启服务以使更改生效") 
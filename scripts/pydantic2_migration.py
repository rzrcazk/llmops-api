#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/10/28
@File    : pydantic2_migration.py
Pydantic 2.x 迁移脚本
"""
import os
import re
from typing import List, Tuple, Pattern

# 根目录路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 只处理这些目录
TARGET_DIRS = ['internal', 'study']

# 导入替换规则
IMPORT_PATTERNS = [
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+BaseModel,\s*Field'),
        'from pydantic import BaseModel, Field'
    ),
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+Field,\s*BaseModel'),
        'from pydantic import BaseModel, Field'
    ),
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+BaseModel'),
        'from pydantic import BaseModel'
    ),
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+Field'),
        'from pydantic import Field'
    ),
    # 新增：处理pydantic.v1导入
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+BaseModel,\s*Field'),
        'from pydantic import BaseModel, Field'
    ),
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+Field,\s*BaseModel'),
        'from pydantic import BaseModel, Field'
    ),
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+BaseModel'),
        'from pydantic import BaseModel'
    ),
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+Field'),
        'from pydantic import Field'
    ),
    # 处理其他常见的pydantic导入
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+validator'),
        'from pydantic import validator'
    ),
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+validator'),
        'from pydantic import validator'
    ),
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+root_validator'),
        'from pydantic import field_validator'
    ),
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+root_validator'),
        'from pydantic import field_validator'
    ),
    # 处理PrivateAttr导入
    (
        re.compile(r'from\s+langchain_core\.pydantic_v1\s+import\s+PrivateAttr'),
        'from pydantic import PrivateAttr'
    ),
    (
        re.compile(r'from\s+pydantic\.v1\s+import\s+PrivateAttr'),
        'from pydantic import PrivateAttr'
    ),
]

# BaseTool子类字段类型注解补全规则 - 更改正则表达式，使其更准确匹配
CLASS_PATTERNS = [
    # name字段类型注解补全 - 调整为更简单直接的匹配，以提高匹配成功率
    (
        re.compile(r'(class\s+\w+\(BaseTool\)[^\n]*\n(?:[ \t]*"""[^"]*"""[ \t]*\n)?)[ \t]*name\s*=\s*(["\'][^"\']*["\'])'),
        r'\1    name: str = \2'
    ),
    # description字段类型注解补全 - 同样简化匹配模式
    (
        re.compile(r'(class\s+\w+\(BaseTool\)[^\n]*\n(?:[ \t]*"""[^"]*"""[ \t]*\n)?)(?:[ \t]*[^\n]*\n)*?[ \t]*description\s*=\s*(["\'][^"\']*["\'])'),
        r'\1    description: str = \2'
    ),
    # args_schema字段类型注解补全 - 两种情况: 已有Type[BaseModel]类型注解和无类型注解
    (
        re.compile(r'(class\s+\w+\(BaseTool\)[^\n]*\n(?:[ \t]*"""[^"]*"""[ \t]*\n)?)(?:[ \t]*[^\n]*\n)*?[ \t]*args_schema\s*=\s*(\w+)(?!\s*:[^=]*)'),
        r'\1    args_schema: type = \2'
    ),
]

# 添加一个更直接的替换模式，用于处理简单的BaseTool字段
DIRECT_REPLACEMENTS = [
    # 直接替换没有类型注解的name字段
    (r'(\s+)name(\s*)=(\s*)([\'\"][^\'\"]*[\'\"])', r'\1name: str\2=\3\4'),
    # 直接替换没有类型注解的description字段
    (r'(\s+)description(\s*)=(\s*)([\'\"][^\'\"]*[\'\"])', r'\1description: str\2=\3\4'),
    # 直接替换没有类型注解的args_schema字段(确保前面没有类型注解)
    (r'(\s+)args_schema(\s*)=(\s*)(\w+)(?!\s*:[^=]*)', r'\1args_schema: type\2=\3\4'),
]

def find_python_files(directory: str, target_dirs: List[str]) -> List[str]:
    """查找指定目录下的所有Python文件"""
    python_files = []
    
    # 只处理指定的目录
    for target_dir in target_dirs:
        target_path = os.path.join(directory, target_dir)
        if not os.path.exists(target_path):
            print(f"目标目录不存在: {target_path}")
            continue
            
        for root, _, files in os.walk(target_path):
            # 跳过.venv目录
            if '.venv' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    
    return python_files

def process_file(file_path: str, patterns: List[Tuple[Pattern, str]]) -> int:
    """处理单个文件，应用所有替换规则"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for pattern, replacement in patterns:
            content = pattern.sub(replacement, content)
        
        # 如果内容有变化，则写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已修改: {file_path}")
            return 1
        return 0
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return 0

def process_basetool_files(file_path: str) -> int:
    """特殊处理BaseTool子类文件，应用更简单直接的替换模式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含BaseTool子类
        if 'class' in content and 'BaseTool' in content:
            original_content = content
            
            # 应用CLASS_PATTERNS
            for pattern, replacement in CLASS_PATTERNS:
                content = pattern.sub(replacement, content)
            
            # 如果上面的规则没有生效，尝试使用更直接的替换
            if content == original_content:
                for pattern, replacement in DIRECT_REPLACEMENTS:
                    # 找到所有BaseTool子类
                    class_matches = re.finditer(r'class\s+\w+\(BaseTool\)[^\{]*?:', content)
                    for class_match in class_matches:
                        class_start = class_match.end()
                        # 找出类定义块的结束位置
                        next_class = content.find('class ', class_start)
                        if next_class == -1:
                            next_class = len(content)
                        
                        # 在类定义块中应用替换
                        class_block = content[class_start:next_class]
                        new_class_block = re.sub(pattern, replacement, class_block)
                        
                        if new_class_block != class_block:
                            content = content[:class_start] + new_class_block + content[next_class:]
            
            # 如果内容有变化，则写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"已修改BaseTool子类: {file_path}")
                return 1
        return 0
    except Exception as e:
        print(f"处理BaseTool子类文件 {file_path} 时出错: {e}")
        return 0

def main():
    """主函数"""
    # 查找所有Python文件
    python_files = find_python_files(ROOT_DIR, TARGET_DIRS)
    print(f"找到 {len(python_files)} 个Python文件")
    
    # 替换导入语句
    import_changes = 0
    for file_path in python_files:
        import_changes += process_file(file_path, IMPORT_PATTERNS)
    print(f"已替换 {import_changes} 个文件的导入语句")
    
    # 补全BaseTool子类字段类型注解 - 使用增强的处理方法
    class_changes = 0
    for file_path in python_files:
        # 先检查文件是否包含BaseTool
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'BaseTool' in content:
                    class_changes += process_basetool_files(file_path)
        except Exception as e:
            print(f"检查文件 {file_path} 是否包含BaseTool时出错: {e}")
    
    print(f"已补全 {class_changes} 个文件的BaseTool子类字段类型注解")

if __name__ == '__main__':
    main()

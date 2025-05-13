#!/bin/bash

# 确保PostgreSQL已安装
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL未安装，请先安装PostgreSQL"
    exit 1
fi

# 数据库连接信息（可根据需要修改）
DB_USER=${PGUSER:-postgres}
DB_HOST=${PGHOST:-localhost}
DB_PORT=${PGPORT:-5432}
DB_NAME=${PGDATABASE:-llmops}
DB_PASS=${PGPASSWORD:-postgres}

# 显示当前使用的连接信息
echo "将使用以下信息连接数据库:"
echo "用户: $DB_USER"
echo "主机: $DB_HOST"
echo "端口: $DB_PORT"
echo "数据库名: $DB_NAME"

# 确认是否继续
echo -n "是否继续? (y/n) "
read answer
if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
    echo "已取消操作"
    exit 0
fi

# 检查数据库是否存在，不存在则创建
echo "正在检查数据库是否存在..."
if ! psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "数据库 $DB_NAME 不存在，正在创建..."
    createdb -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME"
    if [ $? -ne 0 ]; then
        echo "创建数据库失败，请检查连接信息或权限"
        exit 1
    fi
    echo "数据库创建成功!"
else
    echo "数据库 $DB_NAME 已存在"
fi

# 执行SQL初始化脚本
echo "正在初始化数据库结构和账号..."
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -f setup_database.sql

if [ $? -ne 0 ]; then
    echo "数据库初始化失败，请检查错误信息"
    exit 1
fi

echo "数据库初始化完成!"
echo "您现在可以使用账号 gyanzhuan051@gmail.com 和密码 2430@163.com 登录系统。" 
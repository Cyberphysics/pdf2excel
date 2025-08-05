#!/bin/bash

# 紧急停止脚本 - 停止卡住的Docker构建

echo "🚨 紧急停止Docker构建进程..."

# 1. 停止所有Docker构建进程
echo "停止Docker构建进程..."
pkill -f "docker build" 2>/dev/null || echo "没有找到构建进程"

# 2. 停止所有Docker容器
echo "停止所有运行中的容器..."
docker stop $(docker ps -q) 2>/dev/null || echo "没有运行中的容器"

# 3. 清理Docker系统
echo "清理Docker系统..."
docker system prune -f

# 4. 清理构建缓存
echo "清理构建缓存..."
docker builder prune -f

# 5. 显示当前状态
echo "当前Docker状态:"
docker ps -a
docker images

echo "✅ 紧急停止完成！"
echo
echo "🚀 下一步建议:"
echo "   1. 运行 ./vm_quick_build.sh 使用快速构建"
echo "   2. 或手动构建: docker build -t test ."
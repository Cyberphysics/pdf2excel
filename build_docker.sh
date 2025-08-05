#!/bin/bash

# Docker构建脚本 - 专门解决依赖问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🐳 PDF转Excel服务 - Docker构建"
echo "=============================="

# 1. 检查Docker
log_info "检查Docker环境..."
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

docker --version
log_success "Docker环境检查通过"

# 2. 清理旧镜像
log_info "清理旧镜像..."
docker rmi pdf2excel:latest 2>/dev/null || true
docker system prune -f

# 3. 构建镜像
log_info "构建Docker镜像..."
echo "使用以下Dockerfile:"
echo "------------------------"
head -20 Dockerfile
echo "------------------------"

if docker build --no-cache -t pdf2excel:latest .; then
    log_success "Docker镜像构建成功"
else
    log_error "Docker镜像构建失败"
    exit 1
fi

# 4. 测试镜像
log_info "测试Docker镜像..."

# 启动测试容器
docker run -d --name pdf2excel-test -p 5001:5000 pdf2excel:latest

# 等待启动
log_info "等待容器启动..."
sleep 15

# 检查容器状态
if docker ps | grep pdf2excel-test > /dev/null; then
    log_success "容器启动成功"
    
    # 测试API
    log_info "测试API端点..."
    if curl -s http://localhost:5001/api/pdf/diagnose > /dev/null; then
        log_success "API测试通过"
        
        echo
        echo "📊 服务诊断信息:"
        curl -s http://localhost:5001/api/pdf/diagnose | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    print('无法解析JSON响应')
"
    else
        log_error "API测试失败"
        echo "容器日志:"
        docker logs pdf2excel-test
    fi
else
    log_error "容器启动失败"
    echo "容器日志:"
    docker logs pdf2excel-test
fi

# 5. 清理测试容器
log_info "清理测试容器..."
docker stop pdf2excel-test 2>/dev/null || true
docker rm pdf2excel-test 2>/dev/null || true

# 6. 显示镜像信息
echo
log_success "构建完成!"
echo "📦 镜像信息:"
docker images pdf2excel:latest

echo
echo "🚀 使用方法:"
echo "   # 启动服务"
echo "   docker run -d -p 5000:5000 --name pdf2excel pdf2excel:latest"
echo
echo "   # 使用docker-compose"
echo "   docker-compose up -d"
echo
echo "   # 查看日志"
echo "   docker logs pdf2excel"
echo
echo "   # 停止服务"
echo "   docker stop pdf2excel && docker rm pdf2excel"
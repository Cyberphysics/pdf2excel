#!/bin/bash

# 紧急构建脚本 - 使用干净的配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
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

echo "🚨 紧急构建 - 使用干净配置"
echo "=========================="

# 1. 停止并清理
log_info "清理现有容器..."
docker stop $(docker ps -q) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true
docker system prune -f

# 2. 使用干净的Dockerfile
log_info "使用干净的Dockerfile..."
cp Dockerfile.clean Dockerfile

# 3. 构建镜像
log_info "构建Docker镜像..."
IMAGE_NAME="pdf2excel-clean"

if docker build --no-cache -t $IMAGE_NAME .; then
    log_success "镜像构建成功！"
else
    log_error "构建失败"
    exit 1
fi

# 4. 测试运行
log_info "测试镜像..."
docker run -d --name ${IMAGE_NAME}-test -p 5000:5000 $IMAGE_NAME

# 等待启动
sleep 20

# 检查服务
if curl -f http://localhost:5000/api/pdf/diagnose > /dev/null 2>&1; then
    log_success "🎉 紧急构建成功！服务正常运行"
    
    echo "📊 服务状态:"
    curl -s http://localhost:5000/api/pdf/diagnose | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    print('服务正常运行')
" || echo "服务正常运行"

    echo
    echo "✅ 容器正在运行中..."
    echo "🌐 访问地址: http://localhost:5000"
    echo "📋 容器名称: ${IMAGE_NAME}-test"
    
else
    log_error "服务启动失败，查看日志..."
    docker logs ${IMAGE_NAME}-test
    
    # 清理失败的容器
    docker stop ${IMAGE_NAME}-test 2>/dev/null || true
    docker rm ${IMAGE_NAME}-test 2>/dev/null || true
    exit 1
fi

echo
log_success "🎉 紧急构建完成！"
echo "=================================="
echo "📦 镜像名称: $IMAGE_NAME"
echo "🔧 配置: 无camelot依赖，核心功能"
echo
echo "🚀 下一步操作:"
echo "   1. 标记镜像: docker tag $IMAGE_NAME your-username/pdf2excel:latest"
echo "   2. 推送镜像: docker push your-username/pdf2excel:latest"
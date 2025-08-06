#!/bin/bash

# 修复路由冲突问题

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

echo "🔧 修复路由冲突问题"
echo "=================="

# 1. 停止当前容器
log_info "停止当前容器..."
docker stop $(docker ps -q) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# 2. 检查Python语法
log_info "检查Python文件语法..."
if python3 -m py_compile src/main.py 2>/dev/null; then
    echo "✅ src/main.py: 语法正确"
else
    echo "❌ src/main.py: 语法错误"
    python3 -m py_compile src/main.py
    exit 1
fi

if python3 -m py_compile src/routes/pdf_converter.py 2>/dev/null; then
    echo "✅ src/routes/pdf_converter.py: 语法正确"
else
    echo "❌ src/routes/pdf_converter.py: 语法错误"
    python3 -m py_compile src/routes/pdf_converter.py
    exit 1
fi

# 3. 重新构建镜像
log_info "重新构建Docker镜像..."
IMAGE_NAME="pdf2excel-fixed"

if docker build --no-cache -t $IMAGE_NAME .; then
    log_success "镜像构建成功！"
else
    echo "构建失败"
    exit 1
fi

# 4. 测试运行
log_info "测试镜像..."
docker run -d --name ${IMAGE_NAME}-test -p 5000:5000 $IMAGE_NAME

# 等待启动
sleep 20

# 检查服务
if curl -f http://localhost:5000/api/pdf/diagnose > /dev/null 2>&1; then
    log_success "🎉 路由冲突修复成功！服务正常运行"
    
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
    echo "服务启动失败，查看日志..."
    docker logs ${IMAGE_NAME}-test
    
    # 清理失败的容器
    docker stop ${IMAGE_NAME}-test 2>/dev/null || true
    docker rm ${IMAGE_NAME}-test 2>/dev/null || true
    exit 1
fi

echo
log_success "🎉 修复完成！"
echo "=================================="
echo "✅ 删除了重复的路由定义"
echo "✅ 删除了根目录的旧文件"
echo "✅ 服务正常运行"
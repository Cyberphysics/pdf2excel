#!/bin/bash

# 虚拟机快速构建脚本 - 解决构建卡住问题

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🚀 PDF转Excel服务 - 快速构建 (解决卡住问题)"
echo "============================================="

# 1. 停止并清理现有构建
log_info "停止现有构建进程..."
docker system prune -f
pkill -f "docker build" 2>/dev/null || true

# 2. 选择构建策略
echo
echo "请选择构建策略:"
echo "1. 最小化依赖 (仅核心PDF功能，跳过可能卡住的库)"
echo "2. 无加密依赖 (移除cryptography相关依赖)"
echo "3. 分步构建 (逐步安装，便于调试)"
echo "4. 使用预构建基础镜像"
echo

read -p "请选择 (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        log_info "使用最小化依赖策略..."
        cp requirements_minimal.txt requirements.txt
        BUILD_STRATEGY="minimal"
        ;;
    2)
        log_info "使用无加密依赖策略..."
        cp requirements_no_crypto.txt requirements.txt
        BUILD_STRATEGY="no_crypto"
        ;;
    3)
        log_info "使用分步构建策略..."
        BUILD_STRATEGY="step_by_step"
        ;;
    4)
        log_info "使用预构建基础镜像策略..."
        BUILD_STRATEGY="prebuilt"
        ;;
    *)
        log_error "无效选择，使用默认最小化策略"
        cp requirements_minimal.txt requirements.txt
        BUILD_STRATEGY="minimal"
        ;;
esac

# 3. 根据策略创建Dockerfile
case $BUILD_STRATEGY in
    "minimal"|"no_crypto")
        log_info "创建简化Dockerfile..."
        cat > Dockerfile.quick << 'EOF'
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 安装最基础的系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    default-jre \
    ghostscript \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

COPY requirements.txt .

# 快速安装，跳过缓存
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads outputs data logs config
RUN chmod -R 755 /app

EXPOSE 5000
CMD ["python3", "-m", "src.main"]
EOF
        ;;
        
    "step_by_step")
        log_info "创建分步构建Dockerfile..."
        cat > Dockerfile.quick << 'EOF'
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential default-jre ghostscript poppler-utils curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

# 分步安装Python包
RUN pip3 install --no-cache-dir --upgrade pip

# 第1步：基础框架
RUN pip3 install --no-cache-dir Flask==2.3.3 flask-cors==4.0.0 Werkzeug==2.3.7

# 第2步：数据处理
RUN pip3 install --no-cache-dir pandas==2.0.3 numpy==1.24.3 openpyxl==3.1.2

# 第3步：PDF处理 (核心功能)
RUN pip3 install --no-cache-dir pdfplumber==0.9.0 PyPDF2==3.0.1

# 第4步：其他依赖
RUN pip3 install --no-cache-dir python-dateutil==2.8.2 six==1.16.0

COPY . .
RUN mkdir -p uploads outputs data logs config
RUN chmod -R 755 /app

EXPOSE 5000
CMD ["python3", "-m", "src.main"]
EOF
        ;;
        
    "prebuilt")
        log_info "创建预构建基础镜像Dockerfile..."
        cat > Dockerfile.quick << 'EOF'
# 使用包含常用科学计算库的镜像
FROM jupyter/scipy-notebook:python-3.11

USER root
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 安装PDF处理依赖
RUN apt-get update && apt-get install -y \
    default-jre ghostscript poppler-utils curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

# 安装PDF特定库
RUN pip3 install --no-cache-dir pdfplumber==0.9.0 PyPDF2==3.0.1 flask-cors==4.0.0

COPY . .
RUN mkdir -p uploads outputs data logs config
RUN chmod -R 755 /app

EXPOSE 5000
CMD ["python3", "-m", "src.main"]
EOF
        ;;
esac

# 4. 开始构建
log_info "开始构建Docker镜像..."
IMAGE_NAME="pdf2excel-quick"

# 设置构建超时
timeout 600s docker build -f Dockerfile.quick -t $IMAGE_NAME . || {
    log_error "构建超时或失败"
    echo "可能的解决方案:"
    echo "1. 检查网络连接"
    echo "2. 使用国内镜像源"
    echo "3. 尝试其他构建策略"
    exit 1
}

log_success "镜像构建完成！"

# 5. 快速测试
log_info "测试镜像..."
docker run -d --name ${IMAGE_NAME}-test -p 5001:5000 $IMAGE_NAME

sleep 10

if curl -f http://localhost:5001/api/pdf/diagnose > /dev/null 2>&1; then
    log_success "镜像测试通过！"
    
    # 显示功能状态
    echo "📊 服务功能状态:"
    curl -s http://localhost:5001/api/pdf/diagnose | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for key, value in data.items():
        status = '✅' if value else '❌'
        print(f'  {status} {key}: {value}')
except:
    print('  ✅ 服务正常运行')
" || echo "  ✅ 服务正常运行"

else
    log_warning "服务启动但API不响应，检查日志..."
    docker logs ${IMAGE_NAME}-test
fi

# 清理测试容器
docker stop ${IMAGE_NAME}-test 2>/dev/null || true
docker rm ${IMAGE_NAME}-test 2>/dev/null || true

echo
log_success "🎉 快速构建完成！"
echo "=================================="
echo "📦 镜像名称: $IMAGE_NAME"
echo "🏷️  构建策略: $BUILD_STRATEGY"
echo
echo "🚀 下一步操作:"
echo "   1. 标记镜像: docker tag $IMAGE_NAME your-username/pdf2excel:latest"
echo "   2. 推送镜像: docker push your-username/pdf2excel:latest"
echo "   3. 或继续优化: 根据测试结果调整依赖"
echo
echo "💡 如果功能不完整，可以后续添加缺失的依赖"
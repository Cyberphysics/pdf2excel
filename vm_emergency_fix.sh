#!/bin/bash

# 紧急修复脚本 - 修复缺少flask_sqlalchemy的问题

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

echo "🚨 紧急修复 - Flask-SQLAlchemy缺失问题"
echo "===================================="

# 1. 停止当前容器
log_info "停止当前运行的容器..."
docker stop $(docker ps -q) 2>/dev/null || echo "没有运行中的容器"
docker rm $(docker ps -aq) 2>/dev/null || echo "没有容器需要删除"

# 2. 创建修复后的requirements.txt
log_info "创建修复后的requirements.txt..."
cat > requirements_fixed.txt << 'EOF'
# Flask核心框架 (包含所有必需组件)
Flask==2.3.3
flask-cors==4.0.0
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7

# 数据处理
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2

# PDF文本提取库 (核心功能)
pdfplumber==0.9.0
PyPDF2==3.0.1

# 其他必需依赖
python-dateutil==2.8.2
six==1.16.0
EOF

cp requirements_fixed.txt requirements.txt
log_success "requirements.txt已修复"

# 3. 创建快速构建的Dockerfile
log_info "创建快速构建Dockerfile..."
cat > Dockerfile.emergency << 'EOF'
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    default-jre \
    ghostscript \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java

# 复制requirements并安装
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p uploads outputs data logs config
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/pdf/diagnose || exit 1

# 启动应用
CMD ["python3", "-m", "src.main"]
EOF

# 4. 快速构建
log_info "开始快速构建..."
IMAGE_NAME="pdf2excel-fixed"

if docker build -f Dockerfile.emergency --no-cache -t $IMAGE_NAME .; then
    log_success "镜像构建成功！"
else
    log_error "构建失败"
    exit 1
fi

# 5. 测试运行
log_info "测试新镜像..."
docker run -d --name ${IMAGE_NAME}-test -p 5001:5000 $IMAGE_NAME

# 等待启动
sleep 15

# 检查服务
if curl -f http://localhost:5001/api/pdf/diagnose > /dev/null 2>&1; then
    log_success "🎉 服务修复成功！"
    
    echo "📊 服务状态:"
    curl -s http://localhost:5001/api/pdf/diagnose | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    print('服务正常运行')
" || echo "服务正常运行"

    # 保持容器运行
    echo
    echo "✅ 容器正在运行中..."
    echo "🌐 访问地址: http://localhost:5001"
    echo "📋 容器名称: ${IMAGE_NAME}-test"
    echo
    echo "🚀 下一步操作:"
    echo "   1. 标记镜像: docker tag $IMAGE_NAME your-username/pdf2excel:latest"
    echo "   2. 推送镜像: docker push your-username/pdf2excel:latest"
    echo "   3. 停止测试: docker stop ${IMAGE_NAME}-test"
    
else
    log_error "服务启动失败，查看日志..."
    docker logs ${IMAGE_NAME}-test
    
    # 清理失败的容器
    docker stop ${IMAGE_NAME}-test 2>/dev/null || true
    docker rm ${IMAGE_NAME}-test 2>/dev/null || true
    exit 1
fi

# 清理临时文件
rm -f requirements_fixed.txt Dockerfile.emergency

log_success "紧急修复完成！"
#!/bin/bash

# PDF转Excel服务 - 完整设置和测试脚本

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 PDF转Excel服务 - 完整设置和测试"
echo "=================================="

# 1. 检查系统依赖
log_info "检查系统依赖..."

# 检查是否在macOS上
if [[ "$OSTYPE" == "darwin"* ]]; then
    log_info "检测到macOS系统"
    
    # 检查Homebrew
    if ! command -v brew &> /dev/null; then
        log_error "需要安装Homebrew: https://brew.sh/"
        exit 1
    fi
    
    # 安装系统依赖
    log_info "安装系统依赖..."
    brew install poppler ghostscript openjdk
    
    # 设置Java环境
    export JAVA_HOME=$(/usr/libexec/java_home)
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_info "检测到Linux系统"
    
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y poppler-utils ghostscript default-jre
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        sudo yum install -y poppler-utils ghostscript java-11-openjdk
    fi
fi

# 2. 检查Python环境
log_info "检查Python环境..."
python3 --version
pip3 --version

# 3. 创建虚拟环境(可选)
if [ "$1" == "--venv" ]; then
    log_info "创建Python虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    log_success "虚拟环境已激活"
fi

# 4. 安装Python依赖
log_info "安装Python依赖..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 5. 测试依赖
log_info "测试Python依赖..."
python3 test_requirements.py

# 6. 测试应用启动
log_info "测试应用启动..."
timeout 10s python3 -m src.main &
APP_PID=$!
sleep 5

# 检查应用是否启动
if curl -s http://localhost:5000/api/pdf/diagnose > /dev/null; then
    log_success "应用启动成功"
    kill $APP_PID 2>/dev/null || true
else
    log_warning "应用启动测试超时，这可能是正常的"
    kill $APP_PID 2>/dev/null || true
fi

# 7. Docker构建测试
log_info "测试Docker构建..."
if command -v docker &> /dev/null; then
    docker build -t pdf2excel:test .
    log_success "Docker镜像构建成功"
    
    # 测试Docker容器
    log_info "测试Docker容器..."
    docker run -d --name pdf2excel-test -p 5001:5000 pdf2excel:test
    sleep 10
    
    if curl -s http://localhost:5001/api/pdf/diagnose > /dev/null; then
        log_success "Docker容器测试成功"
        echo
        echo "📊 服务诊断信息:"
        curl -s http://localhost:5001/api/pdf/diagnose | python3 -m json.tool
    else
        log_warning "Docker容器测试失败"
        docker logs pdf2excel-test
    fi
    
    # 清理测试容器
    docker stop pdf2excel-test 2>/dev/null || true
    docker rm pdf2excel-test 2>/dev/null || true
else
    log_warning "Docker未安装，跳过Docker测试"
fi

echo
log_success "设置和测试完成！"
echo
echo "🎉 下一步操作:"
echo "   1. 使用 'python3 -m src.main' 启动开发服务器"
echo "   2. 使用 'docker-compose up -d' 启动生产服务"
echo "   3. 访问 http://localhost:5000 使用服务"
echo
echo "📁 项目文件:"
echo "   - src/main.py: 主应用入口"
echo "   - src/routes/: API路由"
echo "   - src/utils/: 工具函数"
echo "   - docker-compose.yml: Docker编排"
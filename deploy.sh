#!/bin/bash

# PDF to Excel Service 部署脚本
# 使用方法: ./deploy.sh [dev|prod]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    directories=("uploads" "outputs" "data" "logs" "config")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "创建目录: $dir"
        fi
    done
    
    # 设置权限
    chmod 755 uploads outputs data logs config
    log_success "目录创建完成"
}

# 构建Docker镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    if docker build -t pdf2excel:latest .; then
        log_success "Docker 镜像构建成功"
    else
        log_error "Docker 镜像构建失败"
        exit 1
    fi
}

# 停止现有服务
stop_service() {
    log_info "停止现有服务..."
    
    if docker-compose ps | grep -q "pdf2excel"; then
        docker-compose down
        log_info "现有服务已停止"
    else
        log_info "没有运行中的服务"
    fi
}

# 启动服务
start_service() {
    local env=${1:-prod}
    
    log_info "启动服务 (环境: $env)..."
    
    if [ "$env" = "dev" ]; then
        # 开发环境：启用调试模式
        FLASK_ENV=development docker-compose up -d
    else
        # 生产环境
        docker-compose up -d
    fi
    
    if [ $? -eq 0 ]; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 等待服务就绪
wait_for_service() {
    log_info "等待服务就绪..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:5000/api/pdf/diagnose > /dev/null 2>&1; then
            log_success "服务已就绪"
            return 0
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_error "服务启动超时"
    return 1
}

# 运行健康检查
health_check() {
    log_info "运行健康检查..."
    
    # 检查服务状态
    if ! curl -s http://localhost:5000/api/pdf/diagnose > /dev/null; then
        log_error "服务健康检查失败"
        return 1
    fi
    
    # 检查PDF处理能力
    local response=$(curl -s http://localhost:5000/api/pdf/diagnose)
    local pdf_libs=$(echo "$response" | grep -o '"pdf_libraries":{[^}]*}' || true)
    
    if [ -n "$pdf_libs" ]; then
        log_success "PDF处理库检查通过"
    else
        log_warning "PDF处理库状态未知"
    fi
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_success "容器状态正常"
    else
        log_error "容器状态异常"
        return 1
    fi
    
    return 0
}

# 显示部署信息
show_deployment_info() {
    log_success "部署完成！"
    echo
    echo "🌐 服务访问地址:"
    echo "   - Web界面: http://localhost:5000"
    echo "   - API文档: http://localhost:5000/api/pdf/diagnose"
    echo
    echo "📊 服务状态:"
    docker-compose ps
    echo
    echo "📝 有用的命令:"
    echo "   - 查看日志: docker-compose logs -f"
    echo "   - 停止服务: docker-compose down"
    echo "   - 重启服务: docker-compose restart"
    echo "   - 进入容器: docker exec -it pdf2excel-service bash"
    echo
    echo "🔍 健康检查:"
    echo "   curl http://localhost:5000/api/pdf/diagnose"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    # 这里可以添加清理逻辑
}

# 主函数
main() {
    local env=${1:-prod}
    
    echo "🚀 PDF to Excel Service 部署脚本"
    echo "=================================="
    echo
    
    # 检查参数
    if [ "$env" != "dev" ] && [ "$env" != "prod" ]; then
        log_error "无效的环境参数: $env (支持: dev, prod)"
        exit 1
    fi
    
    log_info "部署环境: $env"
    echo
    
    # 执行部署步骤
    check_docker
    create_directories
    stop_service
    build_image
    start_service "$env"
    
    if wait_for_service; then
        if health_check; then
            show_deployment_info
        else
            log_warning "健康检查失败，但服务可能仍在启动中"
            log_info "请稍后手动检查服务状态"
        fi
    else
        log_error "部署失败"
        log_info "查看日志: docker-compose logs"
        exit 1
    fi
}

# 信号处理
trap cleanup EXIT

# 执行主函数
main "$@"
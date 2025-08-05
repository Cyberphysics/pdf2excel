#!/bin/bash

# 虚拟机完整工作流 - 拉取代码、构建镜像、推送到DockerHub

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

# 配置变量 - 请根据实际情况修改
REPO_URL="${REPO_URL:-https://github.com/your-username/pdf-to-excel-service.git}"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-your-dockerhub-username}"
IMAGE_NAME="$DOCKERHUB_USERNAME/pdf2excel"
VERSION=$(date +%Y%m%d-%H%M%S)
LATEST_TAG="latest"

echo "🚀 PDF转Excel服务 - 虚拟机构建流程"
echo "=================================="
echo "📦 镜像名称: $IMAGE_NAME"
echo "🏷️  版本标签: $VERSION"
echo "🔗 仓库地址: $REPO_URL"
echo

# 1. 环境检查
log_info "检查环境依赖..."
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    echo "安装命令: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    exit 1
fi

if ! command -v git &> /dev/null; then
    log_error "Git未安装，请先安装Git"
    echo "安装命令: sudo apt-get install -y git"
    exit 1
fi

docker --version
git --version
log_success "环境检查通过"

# 2. 检查Docker登录状态
log_info "检查DockerHub登录状态..."
if ! docker info | grep -q "Username"; then
    log_warning "未登录DockerHub，请先登录"
    echo "登录命令: docker login"
    read -p "是否现在登录? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker login
    else
        log_error "需要登录DockerHub才能推送镜像"
        exit 1
    fi
fi
log_success "DockerHub登录状态正常"

# 3. 拉取最新代码
log_info "拉取最新代码..."
if [ -d "pdf-to-excel-service" ]; then
    cd pdf-to-excel-service
    log_info "更新现有仓库..."
    git fetch origin
    git reset --hard origin/main
    log_success "代码更新完成"
else
    log_info "克隆新仓库..."
    git clone $REPO_URL
    cd pdf-to-excel-service
    log_success "代码克隆完成"
fi

# 显示最新提交信息
echo "📝 最新提交信息:"
git log --oneline -5

# 4. 清理旧镜像
log_info "清理旧镜像..."
docker rmi $IMAGE_NAME:$LATEST_TAG 2>/dev/null || true
docker system prune -f

# 5. 修复依赖冲突
log_info "检查并修复依赖冲突..."
if [ -f "vm_fix_dependencies.sh" ]; then
    log_info "运行依赖修复脚本..."
    chmod +x vm_fix_dependencies.sh
    # 只运行修复部分，不运行测试
    sed -n '1,/# 7. 测试构建/p' vm_fix_dependencies.sh | head -n -1 > temp_fix.sh
    chmod +x temp_fix.sh
    ./temp_fix.sh || log_warning "依赖修复脚本执行有警告，继续构建..."
    rm -f temp_fix.sh
fi

# 6. 构建镜像
log_info "构建Docker镜像..."
echo "🔨 开始构建，这可能需要几分钟..."

if docker build --no-cache -t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:$LATEST_TAG .; then
    log_success "镜像构建完成"
else
    log_error "镜像构建失败"
    echo "尝试使用修复后的配置重新构建..."
    
    # 如果构建失败，尝试使用修复脚本
    if [ -f "vm_fix_dependencies.sh" ]; then
        log_info "使用依赖修复脚本重新构建..."
        ./vm_fix_dependencies.sh
        # 重新标记镜像
        docker tag pdf2excel-test $IMAGE_NAME:$VERSION
        docker tag pdf2excel-test $IMAGE_NAME:$LATEST_TAG
        log_success "使用修复脚本构建完成"
    else
        exit 1
    fi
fi

# 6. 测试镜像
log_info "测试Docker镜像..."
docker run -d --name pdf2excel-test -p 5001:5000 $IMAGE_NAME:$LATEST_TAG

# 等待服务启动
log_info "等待服务启动..."
for i in {1..30}; do
    if curl -f http://localhost:5001/api/pdf/diagnose > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 1
done
echo

# 健康检查
if curl -f http://localhost:5001/api/pdf/diagnose > /dev/null 2>&1; then
    log_success "镜像测试通过"
    
    # 显示诊断信息
    echo "📊 服务诊断信息:"
    curl -s http://localhost:5001/api/pdf/diagnose | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print('服务正常运行，但无法解析诊断信息')
" || echo "服务正常运行"

else
    log_error "镜像测试失败"
    echo "容器日志:"
    docker logs pdf2excel-test
    docker stop pdf2excel-test
    docker rm pdf2excel-test
    exit 1
fi

# 清理测试容器
docker stop pdf2excel-test
docker rm pdf2excel-test

# 7. 推送到DockerHub
log_info "推送镜像到DockerHub..."
echo "📤 推送版本镜像: $IMAGE_NAME:$VERSION"
if docker push $IMAGE_NAME:$VERSION; then
    log_success "版本镜像推送完成"
else
    log_error "版本镜像推送失败"
    exit 1
fi

echo "📤 推送最新镜像: $IMAGE_NAME:$LATEST_TAG"
if docker push $IMAGE_NAME:$LATEST_TAG; then
    log_success "最新镜像推送完成"
else
    log_error "最新镜像推送失败"
    exit 1
fi

# 8. 生成部署信息
log_info "生成部署信息..."
cat > deployment_info.txt << EOF
# PDF转Excel服务部署信息
构建时间: $(date)
Git提交: $(git rev-parse --short HEAD)
镜像版本: $IMAGE_NAME:$VERSION
最新镜像: $IMAGE_NAME:$LATEST_TAG

# 部署命令
docker run -d -p 80:5000 --name pdf2excel $IMAGE_NAME:$LATEST_TAG

# docker-compose部署
version: '3.8'
services:
  pdf2excel:
    image: $IMAGE_NAME:$LATEST_TAG
    ports:
      - "80:5000"
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

# 健康检查
curl http://your-domain.com/api/pdf/diagnose
EOF

# 9. 清理本地镜像
log_info "清理本地镜像..."
docker rmi $IMAGE_NAME:$VERSION 2>/dev/null || true
docker system prune -f

echo
echo "🎉 构建和推送流程完成!"
echo "=================================="
echo "📦 镜像信息:"
echo "   - 版本镜像: $IMAGE_NAME:$VERSION"
echo "   - 最新镜像: $IMAGE_NAME:$LATEST_TAG"
echo
echo "🌐 DockerHub地址:"
echo "   https://hub.docker.com/r/$DOCKERHUB_USERNAME/pdf2excel"
echo
echo "🚀 快速部署命令:"
echo "   docker run -d -p 80:5000 --name pdf2excel $IMAGE_NAME:$LATEST_TAG"
echo
echo "📋 部署信息已保存到: deployment_info.txt"
echo
log_success "所有任务完成！镜像已推送到DockerHub，可以进行生产部署了。"
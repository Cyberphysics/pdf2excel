# PDF转Excel服务 - 完整部署流程

## 🔄 **开发到部署流程**

```
MacBook (开发) → Git推送 → 虚拟机拉取 → Docker构建 → DockerHub推送 → 公网部署
```

## 📋 **流程详细步骤**

### 1️⃣ **MacBook开发阶段**

#### 开发环境准备
```bash
# 安装系统依赖
brew install poppler ghostscript

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip3 install -r requirements.txt

# 本地测试
python3 quick_start.py
```

#### 代码提交流程
```bash
# 1. 检查代码状态
git status

# 2. 添加所有更改
git add .

# 3. 提交更改
git commit -m "feat: 更新PDF转Excel服务功能"

# 4. 推送到远程仓库
git push origin main
```

### 2️⃣ **虚拟机构建阶段**

#### 环境准备脚本
```bash
# vm_setup.sh - 虚拟机初始化脚本
#!/bin/bash

# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Git
sudo apt-get install -y git

# 重启以应用Docker权限
sudo reboot
```

#### 构建和推送脚本
```bash
# vm_build_and_push.sh - 虚拟机构建推送脚本
#!/bin/bash

set -e

# 配置变量
REPO_URL="https://github.com/your-username/pdf-to-excel-service.git"
IMAGE_NAME="your-dockerhub-username/pdf2excel"
VERSION="latest"

echo "🚀 开始构建和推送流程..."

# 1. 拉取最新代码
if [ -d "pdf-to-excel-service" ]; then
    cd pdf-to-excel-service
    git pull origin main
else
    git clone $REPO_URL
    cd pdf-to-excel-service
fi

# 2. 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker build -t $IMAGE_NAME:$VERSION .

# 3. 测试镜像
echo "🧪 测试Docker镜像..."
docker run -d --name test-container -p 5000:5000 $IMAGE_NAME:$VERSION
sleep 10

# 健康检查
if curl -f http://localhost:5000/api/pdf/diagnose; then
    echo "✅ 镜像测试通过"
    docker stop test-container
    docker rm test-container
else
    echo "❌ 镜像测试失败"
    docker logs test-container
    docker stop test-container
    docker rm test-container
    exit 1
fi

# 4. 推送到DockerHub
echo "📤 推送到DockerHub..."
docker push $IMAGE_NAME:$VERSION

echo "🎉 构建和推送完成!"
echo "镜像地址: $IMAGE_NAME:$VERSION"
```

### 3️⃣ **公网部署阶段**

#### 部署配置文件
```yaml
# docker-compose.prod.yml - 生产环境配置
version: '3.8'

services:
  pdf2excel:
    image: your-dockerhub-username/pdf2excel:latest
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
      - MAX_CONTENT_LENGTH=100MB
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/pdf/diagnose"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - pdf2excel
    restart: unless-stopped
```

## 🛠️ **自动化脚本**

### MacBook端脚本
```bash
# deploy_to_production.sh - MacBook端一键部署脚本
#!/bin/bash

set -e

echo "🚀 开始生产部署流程..."

# 1. 本地测试
echo "🧪 运行本地测试..."
python3 quick_start.py &
LOCAL_PID=$!
sleep 5
kill $LOCAL_PID 2>/dev/null || true

# 2. 提交代码
echo "📤 提交代码到Git..."
git add .
git commit -m "deploy: 准备生产部署 $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

# 3. 触发虚拟机构建
echo "🔨 触发虚拟机构建..."
ssh vm-user@your-vm-ip "cd /home/vm-user && ./vm_build_and_push.sh"

# 4. 更新生产环境
echo "🌐 更新生产环境..."
ssh prod-user@your-prod-server "cd /app && docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml up -d"

echo "🎉 部署完成!"
echo "服务地址: https://your-domain.com"
```

### 虚拟机端完整脚本
```bash
# vm_complete_workflow.sh - 虚拟机完整工作流
#!/bin/bash

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

# 配置变量
REPO_URL="https://github.com/your-username/pdf-to-excel-service.git"
IMAGE_NAME="your-dockerhub-username/pdf2excel"
VERSION=$(date +%Y%m%d-%H%M%S)
LATEST_TAG="latest"

echo "🚀 PDF转Excel服务 - 虚拟机构建流程"
echo "=================================="

# 1. 环境检查
log_info "检查环境..."
docker --version || { log_error "Docker未安装"; exit 1; }
git --version || { log_error "Git未安装"; exit 1; }

# 2. 拉取最新代码
log_info "拉取最新代码..."
if [ -d "pdf-to-excel-service" ]; then
    cd pdf-to-excel-service
    git fetch origin
    git reset --hard origin/main
    log_success "代码更新完成"
else
    git clone $REPO_URL
    cd pdf-to-excel-service
    log_success "代码克隆完成"
fi

# 3. 构建镜像
log_info "构建Docker镜像..."
docker build --no-cache -t $IMAGE_NAME:$VERSION -t $IMAGE_NAME:$LATEST_TAG .
log_success "镜像构建完成"

# 4. 测试镜像
log_info "测试Docker镜像..."
docker run -d --name pdf2excel-test -p 5001:5000 $IMAGE_NAME:$LATEST_TAG

# 等待启动
sleep 15

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
except:
    print('服务正常运行')
"
else
    log_error "镜像测试失败"
    docker logs pdf2excel-test
    docker stop pdf2excel-test
    docker rm pdf2excel-test
    exit 1
fi

# 清理测试容器
docker stop pdf2excel-test
docker rm pdf2excel-test

# 5. 推送到DockerHub
log_info "推送到DockerHub..."
echo "请确保已登录DockerHub: docker login"
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:$LATEST_TAG
log_success "镜像推送完成"

# 6. 清理本地镜像
log_info "清理本地镜像..."
docker rmi $IMAGE_NAME:$VERSION 2>/dev/null || true
docker system prune -f

echo
log_success "构建流程完成!"
echo "📦 镜像信息:"
echo "   - 版本镜像: $IMAGE_NAME:$VERSION"
echo "   - 最新镜像: $IMAGE_NAME:$LATEST_TAG"
echo
echo "🌐 部署命令:"
echo "   docker run -d -p 80:5000 --name pdf2excel $IMAGE_NAME:$LATEST_TAG"
echo
echo "🔗 DockerHub地址:"
echo "   https://hub.docker.com/r/$(echo $IMAGE_NAME | cut -d'/' -f1)/$(echo $IMAGE_NAME | cut -d'/' -f2)"
```

## 📝 **使用说明**

### 首次设置

1. **配置Git仓库**
   ```bash
   # 在MacBook上
   cd pdf-to-excel-service
   git remote add origin https://github.com/your-username/pdf-to-excel-service.git
   git push -u origin main
   ```

2. **配置虚拟机**
   ```bash
   # 在虚拟机上运行
   curl -O https://raw.githubusercontent.com/your-username/pdf-to-excel-service/main/vm_setup.sh
   chmod +x vm_setup.sh
   ./vm_setup.sh
   ```

3. **配置DockerHub**
   ```bash
   # 在虚拟机上登录
   docker login
   ```

### 日常部署流程

```bash
# 在MacBook上一键部署
./deploy_to_production.sh
```

或分步执行：

```bash
# 1. MacBook: 提交代码
git add . && git commit -m "update" && git push

# 2. 虚拟机: 构建推送
./vm_complete_workflow.sh

# 3. 生产服务器: 更新服务
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 **故障排除**

### 常见问题

1. **Git推送失败**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **Docker构建失败**
   ```bash
   docker system prune -a
   docker build --no-cache -t test .
   ```

3. **镜像推送失败**
   ```bash
   docker login
   docker tag local-image dockerhub-username/image-name
   docker push dockerhub-username/image-name
   ```

---

**下一步**: 配置你的Git仓库和DockerHub账户信息，然后运行首次设置脚本！
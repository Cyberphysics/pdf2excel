# PDF转Excel服务 - 完整设置指南

## 🎯 **快速开始**

### 1️⃣ **MacBook端设置 (开发环境)**

```bash
# 1. 克隆或进入项目目录
cd pdf-to-excel-service

# 2. 配置Git仓库 (首次设置)
git remote add origin https://github.com/YOUR_USERNAME/pdf-to-excel-service.git

# 3. 安装本地依赖
brew install poppler ghostscript
pip3 install -r requirements.txt

# 4. 本地测试
python3 quick_start.py
```

### 2️⃣ **虚拟机设置 (构建环境)**

```bash
# 1. 安装Docker和Git
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt-get install -y git

# 2. 登录DockerHub
docker login

# 3. 配置环境变量
export REPO_URL="https://github.com/YOUR_USERNAME/pdf-to-excel-service.git"
export DOCKERHUB_USERNAME="YOUR_DOCKERHUB_USERNAME"
```

### 3️⃣ **一键部署**

```bash
# 在MacBook上执行
./deploy_from_macbook.sh
```

## 📋 **详细配置步骤**

### MacBook端配置

#### 1. 环境变量设置
```bash
# 编辑 ~/.zshrc 或 ~/.bash_profile
export VM_HOST="your-vm-ip-address"
export VM_USER="ubuntu"
export VM_SSH_KEY="~/.ssh/id_rsa"
export DOCKERHUB_USERNAME="your-dockerhub-username"
```

#### 2. SSH密钥配置
```bash
# 生成SSH密钥 (如果没有)
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"

# 复制公钥到虚拟机
ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@your-vm-ip
```

#### 3. Git仓库配置
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/pdf-to-excel-service.git
git branch -M main
git push -u origin main
```

### 虚拟机端配置

#### 1. 系统环境准备
```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装必要工具
sudo apt-get install -y curl wget git build-essential

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 重启以应用Docker权限
sudo reboot
```

#### 2. DockerHub配置
```bash
# 登录DockerHub
docker login

# 验证登录状态
docker info | grep Username
```

#### 3. 环境变量配置
```bash
# 创建环境配置文件
cat > ~/.env << EOF
REPO_URL="https://github.com/YOUR_USERNAME/pdf-to-excel-service.git"
DOCKERHUB_USERNAME="YOUR_DOCKERHUB_USERNAME"
EOF

# 加载环境变量
source ~/.env
```

## 🔧 **配置文件模板**

### 1. MacBook端配置 (`~/.zshrc`)
```bash
# PDF转Excel服务配置
export VM_HOST="123.456.789.0"  # 你的虚拟机IP
export VM_USER="ubuntu"         # 虚拟机用户名
export VM_SSH_KEY="~/.ssh/id_rsa"  # SSH私钥路径
export DOCKERHUB_USERNAME="yourusername"  # DockerHub用户名
export REPO_URL="https://github.com/yourusername/pdf-to-excel-service.git"
```

### 2. 虚拟机端配置 (`~/.bashrc`)
```bash
# PDF转Excel服务配置
export REPO_URL="https://github.com/yourusername/pdf-to-excel-service.git"
export DOCKERHUB_USERNAME="yourusername"
```

### 3. 生产环境配置 (`docker-compose.prod.yml`)
```yaml
version: '3.8'
services:
  pdf2excel:
    image: yourusername/pdf2excel:latest
    ports:
      - "80:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

## 🚀 **使用流程**

### 日常开发部署
```bash
# 1. 在MacBook上开发和测试
python3 quick_start.py

# 2. 提交代码并部署
./deploy_from_macbook.sh

# 3. 检查部署状态
curl http://your-domain.com/api/pdf/diagnose
```

### 手动部署流程
```bash
# MacBook: 提交代码
git add . && git commit -m "update" && git push

# 虚拟机: 构建镜像
./vm_complete_workflow.sh

# 生产服务器: 部署服务
docker run -d -p 80:5000 --name pdf2excel yourusername/pdf2excel:latest
```

## 🔍 **验证和测试**

### 1. 本地测试
```bash
# 启动本地服务
python3 quick_start.py

# 测试API
curl http://localhost:5000/api/pdf/diagnose
```

### 2. Docker镜像测试
```bash
# 在虚拟机上测试
docker run -d -p 5000:5000 --name test yourusername/pdf2excel:latest
curl http://localhost:5000/api/pdf/diagnose
docker stop test && docker rm test
```

### 3. 生产环境测试
```bash
# 健康检查
curl http://your-domain.com/api/pdf/diagnose

# 功能测试
curl -X POST -F "file=@test.pdf" http://your-domain.com/api/pdf/upload
```

## 🛠️ **故障排除**

### 常见问题

#### 1. SSH连接失败
```bash
# 检查SSH连接
ssh -v ubuntu@your-vm-ip

# 重新配置SSH密钥
ssh-copy-id ubuntu@your-vm-ip
```

#### 2. Docker构建失败
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker build --no-cache -t test .
```

#### 3. 镜像推送失败
```bash
# 重新登录DockerHub
docker logout
docker login

# 检查镜像标签
docker images
docker tag local-image username/image:latest
docker push username/image:latest
```

#### 4. 服务启动失败
```bash
# 查看容器日志
docker logs pdf2excel

# 检查端口占用
lsof -i :5000

# 重启服务
docker restart pdf2excel
```

## 📊 **监控和维护**

### 1. 服务监控
```bash
# 检查服务状态
docker ps
docker stats pdf2excel

# 查看日志
docker logs -f pdf2excel
```

### 2. 定期维护
```bash
# 更新镜像
docker pull yourusername/pdf2excel:latest
docker-compose -f docker-compose.prod.yml up -d

# 清理旧镜像
docker image prune -a
```

### 3. 备份数据
```bash
# 备份数据卷
docker run --rm -v pdf2excel_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .

# 恢复数据
docker run --rm -v pdf2excel_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /data
```

---

## 🎉 **完成设置后的验证**

1. ✅ MacBook本地测试通过
2. ✅ Git仓库推送成功
3. ✅ 虚拟机构建成功
4. ✅ DockerHub推送成功
5. ✅ 生产环境部署成功
6. ✅ API功能测试通过

**恭喜！你的PDF转Excel服务已经完全配置好了！** 🎊
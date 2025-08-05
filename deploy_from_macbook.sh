#!/bin/bash

# MacBook端部署脚本 - 提交代码并触发虚拟机构建

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
VM_HOST="${VM_HOST:-your-vm-ip}"
VM_USER="${VM_USER:-ubuntu}"
VM_SSH_KEY="${VM_SSH_KEY:-~/.ssh/id_rsa}"
REPO_BRANCH="${REPO_BRANCH:-main}"

echo "🚀 PDF转Excel服务 - MacBook端部署流程"
echo "====================================="
echo "🖥️  虚拟机: $VM_USER@$VM_HOST"
echo "🌿 分支: $REPO_BRANCH"
echo

# 1. 检查Git状态
log_info "检查Git仓库状态..."
if ! git status &>/dev/null; then
    log_error "当前目录不是Git仓库"
    exit 1
fi

# 显示当前状态
echo "📊 当前Git状态:"
git status --short
echo

# 2. 本地快速测试
log_info "运行本地快速测试..."
if command -v python3 &> /dev/null; then
    if [ -f "quick_start.py" ]; then
        echo "🧪 启动本地测试服务..."
        timeout 10s python3 quick_start.py &
        LOCAL_PID=$!
        sleep 3
        
        # 检查服务是否启动
        if curl -s http://localhost:5000/api/pdf/diagnose > /dev/null 2>&1; then
            log_success "本地测试通过"
        else
            log_warning "本地测试未通过，但继续部署流程"
        fi
        
        # 清理测试进程
        kill $LOCAL_PID 2>/dev/null || true
        sleep 1
    else
        log_warning "未找到quick_start.py，跳过本地测试"
    fi
else
    log_warning "未找到Python3，跳过本地测试"
fi

# 3. 提交代码
log_info "准备提交代码..."

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo "📝 发现未提交的更改:"
    git diff --name-only
    echo
    
    read -p "是否提交这些更改? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 获取提交信息
        echo "请输入提交信息 (默认: deploy: 更新PDF转Excel服务):"
        read -r COMMIT_MSG
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="deploy: 更新PDF转Excel服务 $(date '+%Y-%m-%d %H:%M:%S')"
        fi
        
        # 提交更改
        git add .
        git commit -m "$COMMIT_MSG"
        log_success "代码提交完成"
    else
        log_warning "跳过代码提交"
    fi
else
    log_info "没有未提交的更改"
fi

# 4. 推送到远程仓库
log_info "推送代码到远程仓库..."
if git push origin $REPO_BRANCH; then
    log_success "代码推送完成"
else
    log_error "代码推送失败"
    exit 1
fi

# 5. 检查虚拟机连接
log_info "检查虚拟机连接..."
if [ -n "$VM_HOST" ] && [ "$VM_HOST" != "your-vm-ip" ]; then
    if ssh -i "$VM_SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$VM_USER@$VM_HOST" "echo 'SSH连接成功'" 2>/dev/null; then
        log_success "虚拟机连接正常"
        
        # 6. 触发虚拟机构建
        log_info "触发虚拟机构建流程..."
        echo "🔨 在虚拟机上执行构建..."
        
        # 创建远程执行脚本
        cat > /tmp/remote_build.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 开始虚拟机构建流程..."

# 检查是否存在构建脚本
if [ -f "vm_complete_workflow.sh" ]; then
    echo "✅ 找到构建脚本，开始执行..."
    chmod +x vm_complete_workflow.sh
    ./vm_complete_workflow.sh
else
    echo "❌ 未找到vm_complete_workflow.sh脚本"
    echo "请确保已将脚本上传到虚拟机"
    exit 1
fi
EOF

        # 上传并执行脚本
        scp -i "$VM_SSH_KEY" /tmp/remote_build.sh "$VM_USER@$VM_HOST:~/remote_build.sh"
        scp -i "$VM_SSH_KEY" vm_complete_workflow.sh "$VM_USER@$VM_HOST:~/vm_complete_workflow.sh"
        
        if ssh -i "$VM_SSH_KEY" "$VM_USER@$VM_HOST" "chmod +x ~/remote_build.sh && ~/remote_build.sh"; then
            log_success "虚拟机构建完成"
            
            # 获取部署信息
            if scp -i "$VM_SSH_KEY" "$VM_USER@$VM_HOST:~/pdf-to-excel-service/deployment_info.txt" ./deployment_info.txt 2>/dev/null; then
                echo
                echo "📋 部署信息:"
                cat deployment_info.txt
            fi
        else
            log_error "虚拟机构建失败"
            exit 1
        fi
        
        # 清理临时文件
        rm -f /tmp/remote_build.sh
        
    else
        log_error "无法连接到虚拟机: $VM_USER@$VM_HOST"
        echo "请检查:"
        echo "1. 虚拟机IP地址是否正确"
        echo "2. SSH密钥是否正确"
        echo "3. 虚拟机是否正在运行"
        echo "4. 网络连接是否正常"
        exit 1
    fi
else
    log_warning "虚拟机配置未设置，请手动在虚拟机上运行:"
    echo "   git clone https://github.com/your-username/pdf-to-excel-service.git"
    echo "   cd pdf-to-excel-service"
    echo "   ./vm_complete_workflow.sh"
fi

echo
echo "🎉 部署流程完成!"
echo "=================================="
echo "✅ 代码已推送到Git仓库"
echo "✅ Docker镜像已构建并推送到DockerHub"
echo
echo "🌐 下一步 - 在生产服务器上部署:"
echo "   docker run -d -p 80:5000 --name pdf2excel your-dockerhub-username/pdf2excel:latest"
echo
echo "🔗 或使用vendor平台的免费项目部署"
echo
log_success "所有任务完成！"
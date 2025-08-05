#!/bin/bash

# 配置检查脚本 - 验证部署环境配置

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
    echo -e "${GREEN}[✅]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️]${NC} $1"
}

echo "🔍 PDF转Excel服务 - 配置检查"
echo "============================="

# 检查计数器
total_checks=0
passed_checks=0

check_item() {
    total_checks=$((total_checks + 1))
    if eval "$2"; then
        log_success "$1"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        log_error "$1"
        if [ -n "$3" ]; then
            echo "   💡 建议: $3"
        fi
        return 1
    fi
}

echo "📋 MacBook端环境检查"
echo "-------------------"

# 1. 基础工具检查
check_item "Git已安装" "command -v git &> /dev/null" "安装Git: brew install git"
check_item "Python3已安装" "command -v python3 &> /dev/null" "安装Python3: brew install python3"
check_item "curl已安装" "command -v curl &> /dev/null" "curl通常已预装"

# 2. 系统依赖检查
check_item "Homebrew已安装" "command -v brew &> /dev/null" "安装Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
check_item "poppler已安装" "command -v pdfinfo &> /dev/null" "安装poppler: brew install poppler"
check_item "ghostscript已安装" "command -v gs &> /dev/null" "安装ghostscript: brew install ghostscript"

# 3. Git配置检查
echo
echo "📋 Git配置检查"
echo "-------------"

check_item "Git用户名已配置" "[ -n \"\$(git config --global user.name)\" ]" "配置用户名: git config --global user.name 'Your Name'"
check_item "Git邮箱已配置" "[ -n \"\$(git config --global user.email)\" ]" "配置邮箱: git config --global user.email 'your.email@example.com'"

if git remote get-url origin &> /dev/null; then
    log_success "Git远程仓库已配置"
    echo "   🔗 远程仓库: $(git remote get-url origin)"
    passed_checks=$((passed_checks + 1))
else
    log_error "Git远程仓库未配置"
    echo "   💡 建议: git remote add origin https://github.com/YOUR_USERNAME/pdf-to-excel-service.git"
fi
total_checks=$((total_checks + 1))

# 4. Python环境检查
echo
echo "📋 Python环境检查"
echo "----------------"

if [ -f "requirements.txt" ]; then
    log_success "requirements.txt文件存在"
    passed_checks=$((passed_checks + 1))
    
    # 检查关键依赖
    echo "   🔍 检查关键Python包..."
    key_packages=("flask" "pandas" "numpy" "requests")
    for package in "${key_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            echo "   ✅ $package: 已安装"
        else
            echo "   ❌ $package: 未安装"
        fi
    done
else
    log_error "requirements.txt文件不存在"
fi
total_checks=$((total_checks + 1))

# 5. 项目文件检查
echo
echo "📋 项目文件检查"
echo "-------------"

required_files=(
    "src/main.py"
    "src/routes/pdf_converter.py"
    "Dockerfile"
    "docker-compose.yml"
    "vm_complete_workflow.sh"
    "deploy_from_macbook.sh"
)

for file in "${required_files[@]}"; do
    check_item "文件存在: $file" "[ -f \"$file\" ]" "确保项目文件完整"
done

# 6. 环境变量检查
echo
echo "📋 环境变量检查"
echo "-------------"

if [ -n "$VM_HOST" ] && [ "$VM_HOST" != "your-vm-ip" ]; then
    log_success "VM_HOST已配置: $VM_HOST"
    passed_checks=$((passed_checks + 1))
else
    log_warning "VM_HOST未配置或使用默认值"
    echo "   💡 建议: export VM_HOST=\"your-vm-ip-address\""
fi
total_checks=$((total_checks + 1))

if [ -n "$DOCKERHUB_USERNAME" ] && [ "$DOCKERHUB_USERNAME" != "your-dockerhub-username" ]; then
    log_success "DOCKERHUB_USERNAME已配置: $DOCKERHUB_USERNAME"
    passed_checks=$((passed_checks + 1))
else
    log_warning "DOCKERHUB_USERNAME未配置或使用默认值"
    echo "   💡 建议: export DOCKERHUB_USERNAME=\"your-dockerhub-username\""
fi
total_checks=$((total_checks + 1))

# 7. SSH配置检查
echo
echo "📋 SSH配置检查"
echo "------------"

if [ -f "$HOME/.ssh/id_rsa" ]; then
    log_success "SSH私钥存在"
    passed_checks=$((passed_checks + 1))
else
    log_warning "SSH私钥不存在"
    echo "   💡 建议: ssh-keygen -t rsa -b 4096 -C \"your.email@example.com\""
fi
total_checks=$((total_checks + 1))

if [ -n "$VM_HOST" ] && [ "$VM_HOST" != "your-vm-ip" ]; then
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$VM_USER@$VM_HOST" "echo 'SSH连接测试'" 2>/dev/null; then
        log_success "SSH连接到虚拟机正常"
        passed_checks=$((passed_checks + 1))
    else
        log_error "无法SSH连接到虚拟机"
        echo "   💡 建议: ssh-copy-id $VM_USER@$VM_HOST"
    fi
    total_checks=$((total_checks + 1))
fi

# 8. 本地服务测试
echo
echo "📋 本地服务测试"
echo "-------------"

if [ -f "quick_start.py" ]; then
    log_info "尝试启动本地测试服务..."
    if timeout 10s python3 quick_start.py &>/dev/null & then
        sleep 3
        if curl -s http://localhost:5000/api/pdf/diagnose &>/dev/null; then
            log_success "本地服务启动测试通过"
            passed_checks=$((passed_checks + 1))
        else
            log_warning "本地服务启动但API不响应"
        fi
        # 清理测试进程
        pkill -f "python3 quick_start.py" 2>/dev/null || true
    else
        log_warning "本地服务启动测试失败"
    fi
    total_checks=$((total_checks + 1))
fi

# 总结
echo
echo "📊 检查结果总结"
echo "=============="
echo "总检查项: $total_checks"
echo "通过项目: $passed_checks"
echo "通过率: $((passed_checks * 100 / total_checks))%"

if [ $passed_checks -eq $total_checks ]; then
    echo
    log_success "🎉 所有检查项都通过了！你可以开始部署了。"
    echo
    echo "🚀 下一步操作:"
    echo "   1. 运行 ./deploy_from_macbook.sh 开始部署"
    echo "   2. 或者手动提交代码: git add . && git commit -m 'ready for deploy' && git push"
elif [ $passed_checks -gt $((total_checks * 3 / 4)) ]; then
    echo
    log_warning "⚠️  大部分检查项通过，但还有一些需要配置。"
    echo
    echo "🔧 建议优先处理:"
    echo "   1. 配置缺失的环境变量"
    echo "   2. 安装缺失的依赖包"
    echo "   3. 配置SSH连接"
else
    echo
    log_error "❌ 还有较多配置项需要完善。"
    echo
    echo "📖 请参考 SETUP_GUIDE.md 进行详细配置"
fi

echo
echo "📚 相关文档:"
echo "   - SETUP_GUIDE.md: 完整设置指南"
echo "   - DEPLOYMENT_WORKFLOW.md: 部署流程说明"
echo "   - CURRENT_STATUS.md: 项目状态总结"
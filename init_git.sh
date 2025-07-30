#!/bin/bash

# Git仓库初始化脚本

echo "🔧 初始化Git仓库..."

# 检查是否已经是Git仓库
if [ -d ".git" ]; then
    echo "⚠️  当前目录已经是Git仓库"
    read -p "是否要重新初始化？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .git
        echo "✅ 已删除现有Git仓库"
    else
        echo "❌ 取消操作"
        exit 0
    fi
fi

# 初始化Git仓库
git init
echo "✅ Git仓库初始化完成"

# 添加远程仓库
git remote add origin git@github.com:Cyberphysics/pdf2excel.git
echo "✅ 添加远程仓库: git@github.com:Cyberphysics/pdf2excel.git"

# 添加所有文件
git add .
echo "✅ 添加所有文件到暂存区"

# 创建初始提交
git commit -m "Initial commit: PDF to Excel Converter Service

🌟 Features:
- Intelligent PDF parsing with 3-section recognition
- Multi-row description merging
- Standardized 8-field format
- Multi-sheet Excel output
- Order specification comparison
- Docker containerization support
- RESTful API with comprehensive endpoints

🚀 Ready for production deployment"

echo "✅ 创建初始提交"

# 创建主分支
git branch -M main
echo "✅ 设置主分支为 main"

echo
echo "🎉 Git仓库初始化完成！"
echo
echo "📝 下一步操作:"
echo "   1. 确保GitHub仓库已创建: https://github.com/Cyberphysics/pdf2excel"
echo "   2. 推送到远程仓库: git push -u origin main"
echo
echo "🔗 有用的Git命令:"
echo "   - 查看状态: git status"
echo "   - 查看日志: git log --oneline"
echo "   - 推送代码: git push"
echo "   - 拉取代码: git pull"
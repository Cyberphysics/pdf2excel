#!/bin/bash

# 清理开发和测试文件脚本

echo "🧹 清理开发和测试文件..."

# 要删除的文件列表
files_to_remove=(
    "check_elements.js"
    "DEBUG_SUMMARY.md"
    "diagnose_docker_env.py"
    "DIRECTORY_MIGRATION_COMPLETE.md"
    "DOCKER_PDF_PARSING_FIX.md"
    "ENHANCED_PDF_PROCESSING_SUMMARY.md"
    "FINAL_FIX_SUMMARY.md"
    "final_verification.py"
    "fix_path_references.py"
    "fix_spec_routes.py"
    "INTELLIGENT_ROW_MERGING_SUMMARY.md"
    "migrate.py"
    "test_enhanced_parser.py"
    "test_path_integration.py"
    "update_path_references.py"
    "test_*.py"
    "debug_*.py"
    "test_*.pdf"
    "test_*.xlsx"
    "*.tmp"
    "*.temp"
    ".DS_Store"
)

# 要删除的目录列表
dirs_to_remove=(
    "backup_old_structure_*"
    "specs"
    "docs"
    "script"
    ".kiro"
)

# 删除文件
for file in "${files_to_remove[@]}"; do
    if ls $file 1> /dev/null 2>&1; then
        rm -f $file
        echo "✅ 删除文件: $file"
    fi
done

# 删除目录
for dir in "${dirs_to_remove[@]}"; do
    if ls -d $dir 1> /dev/null 2>&1; then
        rm -rf $dir
        echo "✅ 删除目录: $dir"
    fi
done

echo "🎉 清理完成！"
echo
echo "📁 保留的核心文件:"
echo "   - src/              # 源代码"
echo "   - uploads/          # 上传目录"
echo "   - outputs/          # 输出目录"
echo "   - data/             # 数据目录"
echo "   - logs/             # 日志目录"
echo "   - config/           # 配置目录"
echo "   - Dockerfile        # Docker配置"
echo "   - docker-compose.yml # Docker Compose配置"
echo "   - requirements.txt  # Python依赖"
echo "   - README.md         # 项目文档"
echo "   - LICENSE           # 许可证"
echo "   - deploy.sh         # 部署脚本"
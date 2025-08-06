#!/usr/bin/env python3
"""
本地运行脚本 - 解决相对导入问题
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置环境变量
os.environ['PYTHONPATH'] = project_root

if __name__ == '__main__':
    # 使用模块方式运行
    import subprocess
    
    print("🚀 启动PDF转Excel服务 (本地开发模式)")
    print("=" * 40)
    
    try:
        # 使用模块方式运行，避免相对导入问题
        subprocess.run([sys.executable, '-m', 'src.main'], cwd=project_root)
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 请确保:")
        print("1. 已安装所有依赖: pip3 install -r requirements.txt")
        print("2. 在项目根目录运行此脚本")
        print("3. 或使用: python3 -m src.main")
#!/usr/bin/env python3
"""
快速启动脚本 - 用于测试PDF转Excel服务
"""

import sys
import os
import subprocess
import time
import requests
import json

def check_dependencies():
    """检查关键依赖"""
    print("🔍 检查关键依赖...")
    
    try:
        import flask
        import pandas
        import numpy
        print("✅ 基础依赖可用")
        return True
    except ImportError as e:
        print(f"❌ 缺少基础依赖: {e}")
        return False

def start_app():
    """启动应用"""
    print("🚀 启动PDF转Excel服务...")
    
    try:
        # 启动应用
        process = subprocess.Popen([
            sys.executable, "-m", "src.main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待启动
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        # 测试连接
        try:
            response = requests.get("http://localhost:5000/api/pdf/diagnose", timeout=5)
            if response.status_code == 200:
                print("✅ 服务启动成功!")
                print("📊 服务诊断信息:")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
                return process
            else:
                print(f"❌ 服务响应异常: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到服务: {e}")
            return None
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return None

def test_basic_endpoints():
    """测试基本端点"""
    print("\\n🧪 测试基本API端点...")
    
    endpoints = [
        "/api/pdf/diagnose",
        "/api/pdf/health"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5000{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def main():
    """主函数"""
    print("🎯 PDF转Excel服务 - 快速启动测试")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        print("\\n💡 安装依赖:")
        print("pip3 install flask pandas numpy openpyxl requests")
        return False
    
    # 启动应用
    process = start_app()
    if not process:
        return False
    
    # 测试端点
    test_basic_endpoints()
    
    print("\\n🎉 服务运行中!")
    print("📝 可用端点:")
    print("   - http://localhost:5000/api/pdf/diagnose - 服务诊断")
    print("   - http://localhost:5000/api/pdf/health - 健康检查")
    print("   - http://localhost:5000/ - Web界面")
    print("\\n⏹️  按 Ctrl+C 停止服务")
    
    try:
        # 保持运行
        process.wait()
    except KeyboardInterrupt:
        print("\\n🛑 停止服务...")
        process.terminate()
        process.wait()
        print("✅ 服务已停止")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
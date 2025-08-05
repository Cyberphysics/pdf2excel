#!/usr/bin/env python3
"""
测试requirements.txt依赖是否能正确安装和导入
"""
import sys
import importlib
import subprocess

def test_package_installation():
    """测试包安装"""
    print("🔍 测试Python包依赖...")
    
    # 核心包列表
    packages = {
        'Flask': 'flask',
        'flask_cors': 'flask_cors',
        'Flask-SQLAlchemy': 'flask_sqlalchemy',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'openpyxl': 'openpyxl',
        'pdfplumber': 'pdfplumber',
        'pdfminer.six': 'pdfminer',
        'PyPDF2': 'pypdf2',
        'camelot': 'camelot',
        'tabula': 'tabula',
        'cv2': 'cv2',
        'requests': 'requests'
    }
    
    results = {}
    for package_name, import_name in packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}: 导入成功")
            results[package_name] = True
        except ImportError as e:
            print(f"❌ {package_name}: 导入失败 - {e}")
            results[package_name] = False
    
    return results

def test_pdf_libraries():
    """测试PDF处理库的兼容性"""
    print("\n🔍 测试PDF处理库兼容性...")
    
    try:
        import pdfplumber
        import pdfminer
        print(f"✅ pdfplumber版本: {pdfplumber.__version__}")
        print(f"✅ pdfminer版本: {pdfminer.__version__}")
        
        # 检查版本兼容性
        pdfminer_version = pdfminer.__version__
        if pdfminer_version.startswith('20221105') or pdfminer_version.startswith('20231228'):
            print("✅ pdfminer.six版本与pdfplumber兼容")
            return True
        else:
            print(f"⚠️  pdfminer.six版本可能不兼容: {pdfminer_version}")
            return False
            
    except ImportError as e:
        print(f"❌ PDF库导入失败: {e}")
        return False

def test_camelot_dependencies():
    """测试Camelot依赖（可选）"""
    print("\n🔍 测试Camelot依赖（可选）...")
    
    try:
        import camelot
        import cv2
        print(f"✅ camelot版本: {camelot.__version__}")
        print(f"✅ opencv版本: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"⚠️  Camelot依赖未安装（可选功能）: {e}")
        print("   💡 注意: Camelot是可选依赖，不影响核心PDF处理功能")
        return False

def check_system_dependencies():
    """检查系统依赖"""
    print("\n🔍 检查系统依赖...")
    
    commands = {
        'Java': ['java', '-version'],
        'Ghostscript': ['gs', '--version'],
        'pdfinfo': ['pdfinfo', '-v']
    }
    
    results = {}
    for name, cmd in commands.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {name}: 可用")
                results[name] = True
            else:
                print(f"❌ {name}: 不可用")
                results[name] = False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"❌ {name}: 检查失败 - {e}")
            results[name] = False
    
    return results

def generate_fixed_requirements():
    """生成修复后的requirements.txt建议"""
    print("\n🔧 生成修复建议...")
    
    fixed_requirements = """# Flask核心框架 (代码中实际使用)
Flask==2.3.3
flask-cors==4.0.0
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7

# 数据处理 (pandas/numpy兼容版本)
numpy==1.24.3
pandas==2.0.3

# Excel处理 (openpyxl用于样式和注释)
openpyxl==3.1.2

# PDF处理库 (核心功能)
pdfplumber==0.9.0
PyPDF2==3.0.1

# PDF表格提取 (可选，如果构建失败可注释掉)
# camelot-py[cv]==0.10.1
# tabula-py==2.7.0

# 基础依赖
python-dateutil==2.8.2
six==1.16.0

# 开发和测试用 (可选)
requests==2.31.0"""
    
    print("建议的requirements.txt内容:")
    print(fixed_requirements)

def main():
    """主测试函数"""
    print("🧪 开始测试Python依赖...")
    print("=" * 50)
    
    # 测试包安装
    package_results = test_package_installation()
    
    # 测试PDF库兼容性
    pdf_compat = test_pdf_libraries()
    
    # 测试Camelot依赖
    camelot_ok = test_camelot_dependencies()
    
    # 检查系统依赖
    system_results = check_system_dependencies()
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    package_success = sum(package_results.values())
    package_total = len(package_results)
    print(f"Python包: {package_success}/{package_total} 成功")
    
    system_success = sum(system_results.values())
    system_total = len(system_results)
    print(f"系统依赖: {system_success}/{system_total} 可用")
    
    if pdf_compat and camelot_ok and package_success == package_total:
        print("\n🎉 所有依赖测试通过！")
        print("✅ 可以安全构建Docker镜像")
    else:
        print("\n⚠️  存在依赖问题")
        generate_fixed_requirements()
        
        print("\n🔧 修复建议:")
        print("1. 使用修复后的requirements.txt")
        print("2. 确保系统依赖已安装")
        print("3. 重新构建Docker镜像")

if __name__ == "__main__":
    main()
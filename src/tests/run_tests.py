#!/usr/bin/env python3
"""
测试运行器
运行所有单元测试并生成报告
"""

import os
import sys
import unittest
import time
from io import StringIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def run_all_tests():
    """运行所有测试"""
    # 获取测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 发现所有测试
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # 创建测试运行器
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    
    # 记录开始时间
    start_time = time.time()
    
    print("开始运行单元测试...")
    print("=" * 70)
    
    # 运行测试
    result = runner.run(suite)
    
    # 记录结束时间
    end_time = time.time()
    duration = end_time - start_time
    
    # 获取测试输出
    test_output = stream.getvalue()
    
    # 打印测试结果
    print(test_output)
    
    # 打印摘要
    print("=" * 70)
    print(f"测试完成！耗时: {duration:.2f}秒")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    # 如果有失败或错误，打印详细信息
    if result.failures:
        print("\n失败的测试:")
        print("-" * 50)
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)
            print("-" * 50)
    
    if result.errors:
        print("\n错误的测试:")
        print("-" * 50)
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)
            print("-" * 50)
    
    # 返回测试是否全部通过
    return len(result.failures) == 0 and len(result.errors) == 0

def run_specific_test(test_module):
    """运行特定的测试模块"""
    print(f"运行测试模块: {test_module}")
    print("=" * 70)
    
    # 加载特定测试模块
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定测试
        test_module = sys.argv[1]
        success = run_specific_test(test_module)
    else:
        # 运行所有测试
        success = run_all_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
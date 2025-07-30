#!/usr/bin/env python3
"""
集成测试运行器
运行所有集成测试并生成详细报告
"""

import os
import sys
import unittest
import time
from io import StringIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def run_integration_tests():
    """运行所有集成测试"""
    # 获取测试目录
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 发现集成测试
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_integration_*.py')
    
    # 创建测试运行器
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    
    # 记录开始时间
    start_time = time.time()
    
    print("开始运行集成测试...")
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
    print(f"集成测试完成！耗时: {duration:.2f}秒")
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

def run_workflow_tests():
    """运行工作流程集成测试"""
    print("运行工作流程集成测试...")
    print("=" * 70)
    
    # 加载工作流程测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('test_integration_workflow')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def run_api_tests():
    """运行API集成测试"""
    print("运行API集成测试...")
    print("=" * 70)
    
    # 加载API测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('test_integration_api')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def generate_test_report():
    """生成测试报告"""
    print("\n" + "=" * 70)
    print("集成测试报告")
    print("=" * 70)
    
    # 运行各类测试并收集结果
    workflow_success = run_workflow_tests()
    api_success = run_api_tests()
    
    # 生成报告
    print("\n测试结果摘要:")
    print("-" * 30)
    print(f"工作流程测试: {'通过' if workflow_success else '失败'}")
    print(f"API测试: {'通过' if api_success else '失败'}")
    
    overall_success = workflow_success and api_success
    print(f"\n总体结果: {'所有测试通过' if overall_success else '存在测试失败'}")
    
    return overall_success

def main():
    """主函数"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == 'workflow':
            success = run_workflow_tests()
        elif test_type == 'api':
            success = run_api_tests()
        elif test_type == 'report':
            success = generate_test_report()
        else:
            print(f"未知的测试类型: {test_type}")
            print("可用选项: workflow, api, report")
            sys.exit(1)
    else:
        # 运行所有集成测试
        success = run_integration_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
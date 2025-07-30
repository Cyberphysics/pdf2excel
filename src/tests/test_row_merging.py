#!/usr/bin/env python3
"""
测试行合并功能的脚本
"""

import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.pdf_converter import merge_split_rows

def test_description_merging():
    """测试DESCRIPTION字段的合并功能"""
    
    # 创建测试数据：模拟DESCRIPTION字段被分割的情况
    test_data = {
        'ITEM': ['ITEM001', '', '', 'ITEM002', ''],
        'DESCRIPTION': ['办公椅 - 人体工学设计', '可调节高度', '黑色皮质', '办公桌 - 实木材质', '120x60cm'],
        'QTY': [2, '', '', 1, ''],
        'PRICE': [299.99, '', '', 599.00, '']
    }
    
    df = pd.DataFrame(test_data)
    print("原始数据:")
    print(df)
    print("\n" + "="*50 + "\n")
    
    # 应用合并逻辑
    merged_df = merge_split_rows(df)
    print("合并后数据:")
    print(merged_df)
    print("\n" + "="*50 + "\n")
    
    # 验证结果
    expected_descriptions = [
        '办公椅 - 人体工学设计 可调节高度 黑色皮质',
        '办公桌 - 实木材质 120x60cm'
    ]
    
    print("验证结果:")
    for i, expected_desc in enumerate(expected_descriptions):
        if i < len(merged_df):
            actual_desc = merged_df.iloc[i]['DESCRIPTION']
            print(f"行 {i+1}:")
            print(f"  期望: {expected_desc}")
            print(f"  实际: {actual_desc}")
            print(f"  匹配: {'✓' if actual_desc == expected_desc else '✗'}")
        else:
            print(f"行 {i+1}: 缺失")
    
    return merged_df

def test_with_header_detection():
    """测试带表头检测的合并功能"""
    
    # 创建包含表头的测试数据
    test_data = {
        0: ['ITEM', 'ITEM001', '', '', 'ITEM002', ''],
        1: ['DESCRIPTION', '高级办公椅', '人体工学设计', '可调节高度和角度', '实木办公桌', '环保材质'],
        2: ['QTY', '1', '', '', '2', ''],
        3: ['UNIT PRICE', '899.99', '', '', '1299.00', '']
    }
    
    df = pd.DataFrame(test_data)
    print("带表头的原始数据:")
    print(df)
    print("\n" + "="*50 + "\n")
    
    # 应用合并逻辑
    merged_df = merge_split_rows(df)
    print("合并后数据:")
    print(merged_df)
    
    return merged_df

def test_edge_cases():
    """测试边界情况"""
    
    print("测试边界情况:")
    
    # 测试空DataFrame
    empty_df = pd.DataFrame()
    result = merge_split_rows(empty_df)
    print(f"空DataFrame: {len(result)} 行")
    
    # 测试单行DataFrame
    single_row = pd.DataFrame({'DESCRIPTION': ['单行描述'], 'QTY': [1]})
    result = merge_split_rows(single_row)
    print(f"单行DataFrame: {len(result)} 行")
    
    # 测试没有DESCRIPTION列的DataFrame
    no_desc = pd.DataFrame({'ITEM': ['ITEM001'], 'QTY': [1]})
    result = merge_split_rows(no_desc)
    print(f"无DESCRIPTION列: {len(result)} 行")

if __name__ == "__main__":
    print("开始测试行合并功能...\n")
    
    print("测试1: 基本DESCRIPTION合并")
    test_description_merging()
    
    print("\n测试2: 带表头检测的合并")
    test_with_header_detection()
    
    print("\n测试3: 边界情况")
    test_edge_cases()
    
    print("\n测试完成!")
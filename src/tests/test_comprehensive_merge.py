#!/usr/bin/env python3
"""
全面测试行合并功能
"""

import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def merge_split_rows(df):
    """合并被分割的行数据，特别是DESCRIPTION字段"""
    if df.empty:
        return df
    
    # 创建副本避免修改原数据
    df = df.copy()
    
    # 重置索引
    df = df.reset_index(drop=True)
    
    # 如果没有足够的行，直接返回
    if len(df) < 2:
        return df
    
    # 检查是否需要处理表头（第一行是否包含列名关键词且当前列名是数字索引）
    current_columns_are_numeric = all(str(col).isdigit() for col in df.columns)
    first_row_str = ' '.join(str(cell).upper() for cell in df.iloc[0] if pd.notna(cell))
    has_header_in_data = ('DESCRIPTION' in first_row_str or 'ITEM' in first_row_str or 
                         'QTY' in first_row_str or 'PRICE' in first_row_str)
    
    # 只有当前列名是数字索引且第一行包含表头信息时，才将其设为列名
    if current_columns_are_numeric and has_header_in_data:
        # 使用第一行作为列名
        new_columns = []
        header_row = df.iloc[0]
        for col_val in header_row:
            if pd.notna(col_val) and str(col_val).strip():
                new_columns.append(str(col_val).strip())
            else:
                new_columns.append(f'Column_{len(new_columns)}')
        
        # 更新列名
        df.columns = new_columns[:len(df.columns)]
        
        # 删除表头行
        df = df.drop(0).reset_index(drop=True)
    
    # 如果数据行数少于2行，直接返回
    if len(df) < 2:
        return df
    
    # 查找可能的DESCRIPTION列
    description_col = None
    for col in df.columns:
        if 'DESCRIPTION' in str(col).upper() or 'DESC' in str(col).upper():
            description_col = col
            break
    
    if description_col is None:
        return df
    
    # 合并逻辑：识别被分割的行
    merged_rows = []
    i = 0
    
    while i < len(df):
        current_row = df.iloc[i].copy()
        
        # 检查下一行是否是当前行的延续
        j = i + 1
        description_parts = [str(current_row[description_col]) if pd.notna(current_row[description_col]) else '']
        
        while j < len(df):
            next_row = df.iloc[j]
            
            # 判断是否为延续行的条件：
            # 1. 主要字段为空或与当前行相同
            # 2. DESCRIPTION字段有内容
            is_continuation = True
            has_description_content = pd.notna(next_row[description_col]) and str(next_row[description_col]).strip()
            
            # 检查主要字段是否为空（除了DESCRIPTION）
            for col in df.columns:
                if col != description_col:
                    next_val = next_row[col]
                    current_val = current_row[col]
                    
                    # 如果下一行的非DESCRIPTION字段有新的非空值，且与当前行不同，则不是延续行
                    if (pd.notna(next_val) and str(next_val).strip() and 
                        (pd.isna(current_val) or str(next_val).strip() != str(current_val).strip())):
                        # 检查是否是数字字段（可能是数量、价格等）
                        try:
                            float(str(next_val).strip())
                            # 如果是数字且当前行对应字段为空，可能是延续行
                            if pd.isna(current_val) or not str(current_val).strip():
                                continue
                            else:
                                is_continuation = False
                                break
                        except ValueError:
                            # 非数字字段有新内容，不是延续行
                            is_continuation = False
                            break
            
            if is_continuation and has_description_content:
                # 合并DESCRIPTION内容
                description_parts.append(str(next_row[description_col]).strip())
                
                # 合并其他非空字段
                for col in df.columns:
                    if col != description_col and pd.notna(next_row[col]) and str(next_row[col]).strip():
                        if pd.isna(current_row[col]) or not str(current_row[col]).strip():
                            current_row[col] = next_row[col]
                
                j += 1
            else:
                break
        
        # 合并DESCRIPTION内容
        if len(description_parts) > 1:
            # 使用空格连接，去除空内容
            clean_parts = [part for part in description_parts if part and part != 'nan']
            current_row[description_col] = ' '.join(clean_parts)
        
        merged_rows.append(current_row)
        i = j
    
    # 创建新的DataFrame
    if merged_rows:
        result_df = pd.DataFrame(merged_rows)
        # 重置索引
        result_df = result_df.reset_index(drop=True)
        return result_df
    
    return df

def test_real_world_scenario():
    """测试真实世界的场景"""
    print("测试真实世界场景:")
    
    # 模拟PDF提取后的原始数据（类似您遇到的情况）
    test_data = {
        'ITEM': ['ITEM001', '', '', '', 'ITEM002', '', 'ITEM003'],
        'DESCRIPTION': [
            'High Quality Office Chair',
            'Ergonomic Design with',
            'Adjustable Height and',
            'Lumbar Support',
            'Wooden Desk - Premium',
            '120x60cm Surface',
            'File Cabinet'
        ],
        'QTY': [1, '', '', '', 2, '', 1],
        'UNIT_PRICE': [299.99, '', '', '', 599.00, '', 150.00]
    }
    
    df = pd.DataFrame(test_data)
    print("原始数据:")
    print(df)
    print("\n" + "-"*50 + "\n")
    
    # 应用合并逻辑
    merged_df = merge_split_rows(df)
    print("合并后数据:")
    print(merged_df)
    
    # 验证结果
    expected_results = [
        {
            'ITEM': 'ITEM001',
            'DESCRIPTION': 'High Quality Office Chair Ergonomic Design with Adjustable Height and Lumbar Support',
            'QTY': 1,
            'UNIT_PRICE': 299.99
        },
        {
            'ITEM': 'ITEM002', 
            'DESCRIPTION': 'Wooden Desk - Premium 120x60cm Surface',
            'QTY': 2,
            'UNIT_PRICE': 599.00
        },
        {
            'ITEM': 'ITEM003',
            'DESCRIPTION': 'File Cabinet',
            'QTY': 1,
            'UNIT_PRICE': 150.00
        }
    ]
    
    print("\n验证结果:")
    for i, expected in enumerate(expected_results):
        if i < len(merged_df):
            row = merged_df.iloc[i]
            print(f"行 {i+1}:")
            print(f"  ITEM: {row['ITEM']} (期望: {expected['ITEM']}) {'✓' if str(row['ITEM']) == str(expected['ITEM']) else '✗'}")
            print(f"  DESCRIPTION: {row['DESCRIPTION']}")
            print(f"  期望DESCRIPTION: {expected['DESCRIPTION']}")
            print(f"  DESCRIPTION匹配: {'✓' if str(row['DESCRIPTION']) == expected['DESCRIPTION'] else '✗'}")
            print(f"  QTY: {row['QTY']} (期望: {expected['QTY']}) {'✓' if str(row['QTY']) == str(expected['QTY']) else '✗'}")
            print(f"  UNIT_PRICE: {row['UNIT_PRICE']} (期望: {expected['UNIT_PRICE']}) {'✓' if str(row['UNIT_PRICE']) == str(expected['UNIT_PRICE']) else '✗'}")
            print()
    
    return merged_df

def test_edge_cases():
    """测试边界情况"""
    print("\n测试边界情况:")
    
    # 测试1: 没有需要合并的行
    print("1. 没有需要合并的行:")
    test_data = {
        'ITEM': ['ITEM001', 'ITEM002'],
        'DESCRIPTION': ['Chair', 'Desk'],
        'QTY': [1, 2]
    }
    df = pd.DataFrame(test_data)
    result = merge_split_rows(df)
    print(f"原始: {len(df)} 行, 合并后: {len(result)} 行")
    
    # 测试2: 所有行都需要合并
    print("2. 所有行都需要合并:")
    test_data = {
        'ITEM': ['ITEM001', '', ''],
        'DESCRIPTION': ['Part 1', 'Part 2', 'Part 3'],
        'QTY': [1, '', '']
    }
    df = pd.DataFrame(test_data)
    result = merge_split_rows(df)
    print(f"原始: {len(df)} 行, 合并后: {len(result)} 行")
    if len(result) > 0:
        print(f"合并后DESCRIPTION: {result.iloc[0]['DESCRIPTION']}")
    
    # 测试3: 混合情况
    print("3. 混合情况:")
    test_data = {
        'ITEM': ['ITEM001', '', 'ITEM002', 'ITEM003', ''],
        'DESCRIPTION': ['Part 1', 'Part 2', 'Complete Item', 'Part A', 'Part B'],
        'QTY': [1, '', 2, 3, '']
    }
    df = pd.DataFrame(test_data)
    result = merge_split_rows(df)
    print(f"原始: {len(df)} 行, 合并后: {len(result)} 行")
    for i, row in result.iterrows():
        print(f"  行{i+1}: {row['ITEM']} - {row['DESCRIPTION']}")

if __name__ == "__main__":
    print("开始全面测试行合并功能...\n")
    
    test_real_world_scenario()
    test_edge_cases()
    
    print("\n测试完成!")
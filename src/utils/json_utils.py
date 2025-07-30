#!/usr/bin/env python3
"""
JSON工具模块 - 统一处理NaN值和JSON序列化

Steering Rule: 所有API响应都必须通过此模块处理，确保JSON序列化安全
"""

import json
import math
import pandas as pd
import numpy as np
from flask import jsonify

def clean_nan_values(obj):
    """
    递归清理对象中的NaN、Inf和None值，确保JSON序列化安全
    
    Steering Rule: 所有可能包含NaN的数据都必须通过此函数处理
    
    Args:
        obj: 任意Python对象（dict, list, DataFrame等）
        
    Returns:
        清理后的对象，所有NaN/Inf值被替换为None
    """
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(v) for v in obj]
    elif isinstance(obj, pd.DataFrame):
        # DataFrame特殊处理
        return clean_dataframe_nan(obj)
    elif isinstance(obj, pd.Series):
        # Series特殊处理
        return clean_nan_values(obj.tolist())
    elif pd.isna(obj):
        return None
    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    elif isinstance(obj, str) and obj.lower() in ['nan', 'inf', '-inf', 'null']:
        return None
    elif obj is np.nan:
        return None
    else:
        return obj

def clean_dataframe_nan(df):
    """
    专门处理DataFrame中的NaN值
    
    Args:
        df: pandas DataFrame
        
    Returns:
        清理后的数据结构
    """
    if df.empty:
        return {'columns': [], 'data': []}
    
    # 彻底清理DataFrame中的NaN值
    df_clean = df.copy()
    # 使用map替代已弃用的applymap
    df_clean = df_clean.map(lambda x: None if pd.isna(x) or 
                           (isinstance(x, float) and (math.isnan(x) or math.isinf(x))) 
                           else x)
    
    # 转换为字典列表并再次清理
    data_records = df_clean.to_dict('records')
    clean_records = clean_nan_values(data_records)
    
    return {
        'columns': list(df_clean.columns),
        'data': clean_records  # 转换为字典列表格式
    }

def safe_jsonify(data, **kwargs):
    """
    安全的JSON响应生成器
    
    Steering Rule: 所有API响应都应该使用此函数而不是直接使用jsonify
    
    Args:
        data: 要序列化的数据
        **kwargs: jsonify的其他参数
        
    Returns:
        Flask Response对象
    """
    # 清理NaN值
    clean_data = clean_nan_values(data)
    
    # 验证JSON序列化
    try:
        json.dumps(clean_data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        # 如果仍然有序列化问题，返回错误信息
        error_data = {
            'error': 'JSON序列化失败',
            'message': str(e),
            'data_type': str(type(data))
        }
        return jsonify(error_data), 500
    
    return jsonify(clean_data, **kwargs)

def prepare_preview_data(extracted_data, max_rows=20):
    """
    统一的预览数据准备函数
    
    Args:
        extracted_data: 提取的表格数据列表
        max_rows: 最大显示行数
        
    Returns:
        清理后的预览数据
    """
    preview_data = []
    
    for table_info in extracted_data:
        df = table_info['data']
        if df.empty:
            continue
            
        # 限制显示行数
        preview_df = df.head(max_rows)
        
        # 清理数据
        clean_result = clean_dataframe_nan(preview_df)
        
        preview_data.append({
            'table_index': table_info.get('table_index', 1),
            'page': table_info.get('page', 1),
            'accuracy': table_info.get('accuracy', 0.8),
            'columns': clean_result['columns'],
            'data': [list(row.values()) for row in clean_result['data']],  # 转换为二维数组
            'total_rows': len(df),
            'total_columns': len(df.columns)
        })
    
    return preview_data

def prepare_sheet_data(df, sheet_name=None):
    """
    统一的工作表数据准备函数
    
    Args:
        df: pandas DataFrame
        sheet_name: 工作表名称
        
    Returns:
        清理后的工作表数据
    """
    if df.empty:
        return {
            'columns': [],
            'data': [],
            'total_rows': 0,
            'sheet_name': sheet_name or 'Sheet1'
        }
    
    # 清理数据
    clean_result = clean_dataframe_nan(df)
    
    return {
        'columns': clean_result['columns'],
        'data': clean_result['data'],
        'total_rows': len(df),
        'sheet_name': sheet_name or 'Sheet1'
    }

# 导出的主要函数
__all__ = [
    'clean_nan_values',
    'clean_dataframe_nan', 
    'safe_jsonify',
    'prepare_preview_data',
    'prepare_sheet_data'
]
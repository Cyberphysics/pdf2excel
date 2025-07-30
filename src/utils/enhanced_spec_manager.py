"""
增强型产品规格管理模块
支持灵活的列名映射和验证
"""

import os
import uuid
import datetime
import json
from werkzeug.utils import secure_filename
from flask import current_app
import pandas as pd
import numpy as np
from difflib import get_close_matches

from src.utils.config_loader import ConfigLoader

class MappingResult:
    """列名映射结果类"""
    def __init__(self):
        self.success = False  # 映射是否成功
        self.mapped_columns = {}  # 原始列名 -> 标准列名的映射
        self.missing_required = []  # 缺失的必需列
        self.unmapped_columns = []  # 无法映射的列
        self.suggestions = {}  # 针对无法映射列的建议

class EnhancedProductSpecManager:
    def __init__(self, specs_dir='specs'):
        self.specs_dir = specs_dir
        self.ensure_specs_dir()
        self.load_column_mappings()
        
    def ensure_specs_dir(self):
        """确保规格表存储目录存在"""
        if not os.path.exists(self.specs_dir):
            os.makedirs(self.specs_dir)
    
    def load_column_mappings(self):
        """加载列名映射配置"""
        config = ConfigLoader.get_column_mappings()
        self.column_mappings = config.get('column_mappings', {})
        self.required_columns = config.get('required_columns', [])
        self.optional_columns = config.get('optional_columns', [])
        
        # 如果配置为空，使用默认值
        if not self.column_mappings:
            self.column_mappings = {
                'item_id': ['产品ID', '商品编号', '货号'],
                'product_name': ['产品名称', '商品名称', '名称'],
                'size': ['尺寸', '规格', '型号'],
                'color': ['颜色', '色彩'],
                'standard_unit_price': ['标准单价', '单价', '价格']
            }
        
        if not self.required_columns:
            self.required_columns = ['item_id', 'product_name', 'standard_unit_price']
            
        if not self.optional_columns:
            self.optional_columns = ['size', 'color']
    
    def allowed_file(self, filename):
        """检查文件是否为允许的Excel格式"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ['xlsx', 'xls']
    
    def map_columns(self, df):
        """
        映射DataFrame的列名到标准列名
        
        Args:
            df: pandas DataFrame对象
            
        Returns:
            MappingResult: 映射结果对象
        """
        result = MappingResult()
        original_columns = list(df.columns)
        
        # 创建反向映射字典，用于快速查找
        reverse_mapping = {}
        for standard_col, aliases in self.column_mappings.items():
            for alias in aliases:
                reverse_mapping[alias.lower()] = standard_col
            # 标准列名自身也是一个有效的映射
            reverse_mapping[standard_col.lower()] = standard_col
        
        # 尝试映射每一列
        for col in original_columns:
            # 检查精确匹配
            if col.lower() in reverse_mapping:
                standard_col = reverse_mapping[col.lower()]
                result.mapped_columns[col] = standard_col
            else:
                # 尝试模糊匹配
                all_possible_names = list(reverse_mapping.keys())
                matches = get_close_matches(col.lower(), all_possible_names, n=3, cutoff=0.6)
                
                if matches:
                    # 找到了可能的匹配
                    best_match = matches[0]
                    standard_col = reverse_mapping[best_match]
                    result.mapped_columns[col] = standard_col
                    # 记录建议，但仍然使用这个映射
                    result.suggestions[col] = {
                        'mapped_to': standard_col,
                        'confidence': 'medium',
                        'suggestions': [reverse_mapping[m] for m in matches]
                    }
                else:
                    # 无法映射
                    result.unmapped_columns.append(col)
                    
                    # 生成建议 - 使用更智能的算法
                    all_standard_cols = list(self.column_mappings.keys())
                    
                    # 1. 尝试使用difflib的get_close_matches
                    col_suggestions = get_close_matches(col.lower(), 
                                                      [c.lower() for c in all_standard_cols], 
                                                      n=3, 
                                                      cutoff=0.4)
                    
                    # 2. 尝试使用部分匹配
                    if not col_suggestions:
                        for std_col in all_standard_cols:
                            # 检查列名是否包含标准列名
                            if std_col.lower() in col.lower() or col.lower() in std_col.lower():
                                col_suggestions.append(std_col.lower())
                    
                    # 3. 尝试使用词干提取（简化版）
                    if not col_suggestions:
                        # 简单的词干提取：移除常见后缀
                        simplified_col = col.lower()
                        for suffix in ['_id', 'id', '_name', 'name', '_code', 'code', '_price', 'price']:
                            if simplified_col.endswith(suffix):
                                simplified_col = simplified_col[:-len(suffix)]
                                break
                        
                        for std_col in all_standard_cols:
                            simplified_std = std_col.lower()
                            for suffix in ['_id', 'id', '_name', 'name', '_code', 'code', '_price', 'price']:
                                if simplified_std.endswith(suffix):
                                    simplified_std = simplified_std[:-len(suffix)]
                                    break
                            
                            if simplified_col == simplified_std or simplified_col in simplified_std or simplified_std in simplified_col:
                                col_suggestions.append(std_col.lower())
                    
                    # 去重并限制数量
                    col_suggestions = list(dict.fromkeys(col_suggestions))[:3]
                    
                    if col_suggestions:
                        result.suggestions[col] = {
                            'mapped_to': None,
                            'confidence': 'low',
                            'suggestions': [all_standard_cols[[c.lower() for c in all_standard_cols].index(s)] 
                                          if s in [c.lower() for c in all_standard_cols] 
                                          else s 
                                          for s in col_suggestions]
                        }
        
        # 检查是否所有必需列都已映射
        mapped_standard_cols = set(result.mapped_columns.values())
        for required_col in self.required_columns:
            if required_col not in mapped_standard_cols:
                result.missing_required.append(required_col)
        
        # 设置映射结果状态
        result.success = len(result.missing_required) == 0
        
        return result
    
    def create_mapped_dataframe(self, df, mapping_result):
        """
        根据映射结果创建新的DataFrame
        
        Args:
            df: 原始DataFrame
            mapping_result: 映射结果对象
            
        Returns:
            pandas.DataFrame: 映射后的DataFrame
        """
        # 创建一个新的空DataFrame
        mapped_df = pd.DataFrame()
        
        # 复制映射的列
        for original_col, standard_col in mapping_result.mapped_columns.items():
            mapped_df[standard_col] = df[original_col]
        
        # 对于缺失的必需列，添加空列
        for col in mapping_result.missing_required:
            mapped_df[col] = np.nan
            
        return mapped_df
    
    def validate_mapped_dataframe(self, df):
        """
        验证映射后的DataFrame
        
        Args:
            df: 映射后的DataFrame
            
        Returns:
            dict: 验证结果，包含详细的错误信息和建议
        """
        errors = []
        warnings = []
        suggestions = {}
        
        # 检查必需列是否存在
        missing_required = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_required.append(col)
                
        if missing_required:
            error_msg = f'缺少必需的列: {", ".join(missing_required)}'
            errors.append(error_msg)
            suggestions['missing_columns'] = {
                'message': '请添加以下必需列',
                'columns': missing_required
            }
        
        # 如果缺少必需列，直接返回错误
        if errors:
            return {
                'valid': False, 
                'error': '; '.join(errors),
                'warnings': warnings,
                'suggestions': suggestions
            }
        
        # 检查数据类型和有效性
        data_errors = {}
        
        # 检查item_id列
        if 'item_id' in df.columns:
            # 检查空值
            null_indices = df.index[df['item_id'].isnull()].tolist()
            if null_indices:
                row_numbers = [i + 2 for i in null_indices]  # +2 因为Excel从1开始，且有标题行
                error_msg = f'item_id列存在空值 (行: {", ".join(map(str, row_numbers))})'
                errors.append(error_msg)
                data_errors['item_id'] = {
                    'type': 'null_values',
                    'rows': row_numbers,
                    'message': '这些行的产品ID不能为空'
                }
                
            # 检查重复值
            duplicates = df['item_id'].duplicated()
            duplicate_indices = df.index[duplicates].tolist()
            if duplicate_indices:
                row_numbers = [i + 2 for i in duplicate_indices]
                duplicate_values = df.loc[duplicate_indices, 'item_id'].tolist()
                warning_msg = f'item_id列存在重复值: {", ".join(map(str, duplicate_values))} (行: {", ".join(map(str, row_numbers))})'
                warnings.append(warning_msg)
                if 'item_id' not in data_errors:
                    data_errors['item_id'] = {
                        'type': 'duplicate_values',
                        'rows': row_numbers,
                        'values': duplicate_values,
                        'message': '这些产品ID有重复，可能导致数据混淆'
                    }
        
        # 检查product_name列
        if 'product_name' in df.columns:
            null_indices = df.index[df['product_name'].isnull()].tolist()
            if null_indices:
                row_numbers = [i + 2 for i in null_indices]
                warning_msg = f'product_name列存在空值 (行: {", ".join(map(str, row_numbers))})'
                warnings.append(warning_msg)
                data_errors['product_name'] = {
                    'type': 'null_values',
                    'rows': row_numbers,
                    'message': '这些行的产品名称为空，建议填写'
                }
        
        # 检查standard_unit_price列
        if 'standard_unit_price' in df.columns:
            # 尝试转换为数值类型
            try:
                # 先检查哪些值无法转换为数字
                numeric_mask = pd.to_numeric(df['standard_unit_price'], errors='coerce').isnull() & ~df['standard_unit_price'].isnull()
                non_numeric_indices = df.index[numeric_mask].tolist()
                
                if non_numeric_indices:
                    row_numbers = [i + 2 for i in non_numeric_indices]
                    non_numeric_values = df.loc[non_numeric_indices, 'standard_unit_price'].tolist()
                    error_msg = f'standard_unit_price列包含非数字值: {", ".join(map(str, non_numeric_values))} (行: {", ".join(map(str, row_numbers))})'
                    errors.append(error_msg)
                    data_errors['standard_unit_price'] = {
                        'type': 'invalid_type',
                        'rows': row_numbers,
                        'values': non_numeric_values,
                        'message': '这些单价值必须是数字'
                    }
                
                # 检查负值
                df_numeric = df.copy()
                df_numeric['standard_unit_price'] = pd.to_numeric(df_numeric['standard_unit_price'], errors='coerce')
                negative_indices = df_numeric.index[df_numeric['standard_unit_price'] < 0].tolist()
                
                if negative_indices:
                    row_numbers = [i + 2 for i in negative_indices]
                    negative_values = df_numeric.loc[negative_indices, 'standard_unit_price'].tolist()
                    warning_msg = f'standard_unit_price列包含负值: {", ".join(map(str, negative_values))} (行: {", ".join(map(str, row_numbers))})'
                    warnings.append(warning_msg)
                    if 'standard_unit_price' not in data_errors:
                        data_errors['standard_unit_price'] = {
                            'type': 'negative_values',
                            'rows': row_numbers,
                            'values': negative_values,
                            'message': '这些单价为负值，请确认是否正确'
                        }
                    
            except Exception as e:
                errors.append(f'standard_unit_price列数据类型验证失败: {str(e)}')
        
        # 如果有错误，返回详细信息
        if errors:
            return {
                'valid': False, 
                'error': '; '.join(errors),
                'warnings': warnings,
                'data_errors': data_errors,
                'suggestions': suggestions
            }
        
        # 如果只有警告，仍然视为有效，但返回警告信息
        result = {
            'valid': True,
            'record_count': len(df),
            'columns': list(df.columns)
        }
        
        if warnings:
            result['warnings'] = warnings
            result['data_errors'] = data_errors
            
        return result
    
    def upload_spec(self, file):
        """
        上传产品规格表，支持列名映射
        
        Args:
            file: 上传的文件对象
            
        Returns:
            dict: 包含spec_id和filename的字典，或错误信息
        """
        try:
            if not file or file.filename == '':
                return {
                    'error': '未选择文件',
                    'error_code': 'NO_FILE_SELECTED',
                    'message': '请选择一个有效的Excel文件上传'
                }
                
            if not self.allowed_file(file.filename):
                return {
                    'error': '文件格式不支持，请上传Excel文件(.xlsx或.xls)',
                    'error_code': 'INVALID_FILE_FORMAT',
                    'message': '只支持.xlsx或.xls格式的Excel文件'
                }
                
            # 生成唯一的文件ID
            spec_id = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            
            # 保持原始文件扩展名
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            stored_filename = f"{spec_id}.{file_extension}"
            
            # 保存文件
            file_path = os.path.join(self.specs_dir, stored_filename)
            file.save(file_path)
            
            # 验证Excel文件是否可以正常读取
            try:
                df = pd.read_excel(file_path)
                if df.empty:
                    os.remove(file_path)
                    return {
                        'error': 'Excel文件为空或格式不正确',
                        'error_code': 'EMPTY_EXCEL_FILE',
                        'message': '上传的Excel文件不包含任何数据，请检查文件内容'
                    }
                
                # 尝试映射列名
                mapping_result = self.map_columns(df)
                
                # 如果映射失败，返回错误信息
                if not mapping_result.success:
                    os.remove(file_path)
                    
                    # 构建详细的错误信息
                    error_msg = f'Excel文件缺少必需的列: {", ".join(mapping_result.missing_required)}'
                    
                    # 构建结构化的建议信息
                    structured_suggestions = {}
                    if mapping_result.suggestions:
                        column_suggestions = []
                        for col, suggestion in mapping_result.suggestions.items():
                            if suggestion['mapped_to'] is None and col in mapping_result.unmapped_columns:
                                sugg_list = [f"'{s}'" for s in suggestion['suggestions']]
                                sugg_str = f"'{col}' 可能是 {', '.join(sugg_list)}"
                                column_suggestions.append(sugg_str)
                                
                                # 添加结构化建议
                                structured_suggestions[col] = {
                                    'possible_mappings': suggestion['suggestions'],
                                    'confidence': suggestion['confidence']
                                }
                        
                        if column_suggestions:
                            error_msg += "\n\n建议修改列名:\n" + "\n".join(column_suggestions)
                    
                    return {
                        'error': error_msg,
                        'error_code': 'MISSING_REQUIRED_COLUMNS',
                        'message': f'文件缺少必需的列: {", ".join(mapping_result.missing_required)}',
                        'mapping_result': mapping_result.__dict__,
                        'structured_suggestions': structured_suggestions,
                        'required_columns': self.required_columns,
                        'missing_columns': mapping_result.missing_required
                    }
                
                # 创建映射后的DataFrame
                mapped_df = self.create_mapped_dataframe(df, mapping_result)
                
                # 验证映射后的DataFrame
                validation_result = self.validate_mapped_dataframe(mapped_df)
                if not validation_result['valid']:
                    os.remove(file_path)
                    
                    # 生成修改建议
                    correction_suggestions = self.suggest_corrections(df, validation_result)
                    
                    # 确定错误类型
                    error_code = 'DATA_VALIDATION_ERROR'
                    if 'data_errors' in validation_result:
                        data_errors = validation_result['data_errors']
                        if 'item_id' in data_errors and data_errors['item_id']['type'] == 'null_values':
                            error_code = 'NULL_ITEM_ID_VALUES'
                        elif 'standard_unit_price' in data_errors and data_errors['standard_unit_price']['type'] == 'invalid_type':
                            error_code = 'INVALID_PRICE_FORMAT'
                    
                    return {
                        'error': validation_result['error'],
                        'error_code': error_code,
                        'message': '数据验证失败，请查看详细错误信息',
                        'warnings': validation_result.get('warnings', []),
                        'data_errors': validation_result.get('data_errors', {}),
                        'suggestions': correction_suggestions
                    }
                
                # 保存映射后的DataFrame
                mapped_file_path = os.path.join(self.specs_dir, f"{spec_id}_mapped.xlsx")
                mapped_df.to_excel(mapped_file_path, index=False)
                
                # 创建元数据文件
                metadata = {
                    'spec_id': spec_id,
                    'original_filename': original_filename,
                    'stored_filename': stored_filename,
                    'mapped_filename': f"{spec_id}_mapped.xlsx",
                    'upload_time': datetime.datetime.now().isoformat(),
                    'file_size': os.path.getsize(file_path),
                    'record_count': len(df),
                    'column_mapping': mapping_result.mapped_columns
                }
                
                metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                # 构建成功响应
                response = {
                    'spec_id': spec_id,
                    'filename': original_filename,
                    'record_count': len(df),
                    'upload_time': metadata['upload_time'],
                    'mapping_applied': True,
                    'mapped_columns': mapping_result.mapped_columns
                }
                
                # 如果有列映射，添加映射信息
                if mapping_result.mapped_columns:
                    response['column_mapping_details'] = {
                        'original_to_standard': mapping_result.mapped_columns,
                        'mapping_count': len(mapping_result.mapped_columns)
                    }
                
                return response
                
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    'error': f'Excel文件处理失败: {str(e)}',
                    'error_code': 'EXCEL_PROCESSING_ERROR',
                    'message': '无法处理Excel文件，请检查文件格式是否正确',
                    'details': str(e)
                }
            
        except Exception as e:
            return {
                'error': f'上传失败: {str(e)}',
                'error_code': 'UPLOAD_FAILED',
                'message': '文件上传过程中发生错误',
                'details': str(e)
            }
    
    def validate_spec_format(self, file_path):
        """
        验证规格表文件格式
        
        Args:
            file_path: 规格表文件路径
            
        Returns:
            dict: 验证结果
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            if df.empty:
                return {'valid': False, 'error': 'Excel文件为空'}
            
            # 尝试映射列名
            mapping_result = self.map_columns(df)
            
            # 如果映射失败，返回错误信息
            if not mapping_result.success:
                error_msg = f'Excel文件缺少必需的列: {", ".join(mapping_result.missing_required)}'
                
                # 添加建议信息
                suggestions = {}
                if mapping_result.suggestions:
                    column_suggestions = []
                    for col, suggestion in mapping_result.suggestions.items():
                        if suggestion['mapped_to'] is None and col in mapping_result.unmapped_columns:
                            sugg_list = [f"'{s}'" for s in suggestion['suggestions']]
                            sugg_str = f"'{col}' 可能是 {', '.join(sugg_list)}"
                            column_suggestions.append(sugg_str)
                    
                    if column_suggestions:
                        suggestions['column_mapping'] = {
                            'message': '建议修改列名',
                            'suggestions': column_suggestions
                        }
                
                return {
                    'valid': False, 
                    'error': error_msg,
                    'mapping_result': mapping_result.__dict__,
                    'suggestions': suggestions
                }
            
            # 创建映射后的DataFrame
            mapped_df = self.create_mapped_dataframe(df, mapping_result)
            
            # 验证映射后的DataFrame
            validation_result = self.validate_mapped_dataframe(mapped_df)
            
            # 如果验证失败，返回错误信息
            if not validation_result['valid']:
                # 生成修改建议
                correction_suggestions = self.suggest_corrections(df, validation_result)
                
                return {
                    'valid': False,
                    'error': validation_result['error'],
                    'warnings': validation_result.get('warnings', []),
                    'data_errors': validation_result.get('data_errors', {}),
                    'suggestions': correction_suggestions
                }
            
            # 如果有警告，添加到结果中
            result = {
                'valid': True,
                'record_count': validation_result['record_count'],
                'columns': validation_result['columns'],
                'mapped_columns': mapping_result.mapped_columns
            }
            
            if 'warnings' in validation_result:
                result['warnings'] = validation_result['warnings']
                result['data_errors'] = validation_result.get('data_errors', {})
            
            return result
            
        except Exception as e:
            return {'valid': False, 'error': f'验证规格表格式失败: {str(e)}'}
    
    def get_spec_path(self, spec_id, use_mapped=True):
        """
        根据spec_id获取规格表文件路径
        
        Args:
            spec_id: 规格表ID
            use_mapped: 是否使用映射后的文件
            
        Returns:
            str: 文件路径，如果不存在则返回None
        """
        try:
            metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
            
            if not os.path.exists(metadata_path):
                return None
                
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if use_mapped and 'mapped_filename' in metadata:
                excel_path = os.path.join(self.specs_dir, metadata['mapped_filename'])
                if os.path.exists(excel_path):
                    return excel_path
            
            # 如果没有映射文件或不使用映射文件，返回原始文件
            excel_path = os.path.join(self.specs_dir, metadata['stored_filename'])
            
            if os.path.exists(excel_path):
                return excel_path
            else:
                return None
                
        except Exception as e:
            current_app.logger.error(f"获取规格表路径失败: {spec_id}, 错误: {str(e)}")
            return None
    
    def list_specs(self):
        """
        获取所有已上传的产品规格表列表
        
        Returns:
            list: 规格表信息列表
        """
        try:
            specs = []
            
            for filename in os.listdir(self.specs_dir):
                if filename.endswith('.json'):
                    metadata_path = os.path.join(self.specs_dir, filename)
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # 检查对应的Excel文件是否存在
                        excel_path = os.path.join(self.specs_dir, metadata['stored_filename'])
                        if os.path.exists(excel_path):
                            specs.append({
                                'spec_id': metadata['spec_id'],
                                'filename': metadata['original_filename'],
                                'upload_time': metadata['upload_time'],
                                'file_size': metadata.get('file_size', 0),
                                'record_count': metadata.get('record_count', 0),
                                'has_mapping': 'mapped_filename' in metadata
                            })
                    except Exception as e:
                        current_app.logger.warning(f"读取规格表元数据失败: {filename}, 错误: {str(e)}")
                        continue
            
            # 按上传时间倒序排列
            specs.sort(key=lambda x: x['upload_time'], reverse=True)
            return specs
            
        except Exception as e:
            current_app.logger.error(f"获取规格表列表失败: {str(e)}")
            return []
    
    def delete_spec(self, spec_id):
        """
        删除产品规格表
        
        Args:
            spec_id: 规格表ID
            
        Returns:
            dict: 成功或错误信息
        """
        try:
            metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
            
            if not os.path.exists(metadata_path):
                return {'error': '规格表不存在'}
                
            # 读取元数据获取文件名
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # 删除原始Excel文件
            excel_path = os.path.join(self.specs_dir, metadata['stored_filename'])
            if os.path.exists(excel_path):
                os.remove(excel_path)
            
            # 删除映射后的Excel文件（如果存在）
            if 'mapped_filename' in metadata:
                mapped_path = os.path.join(self.specs_dir, metadata['mapped_filename'])
                if os.path.exists(mapped_path):
                    os.remove(mapped_path)
                
            # 删除元数据文件
            os.remove(metadata_path)
            
            return {'message': '规格表删除成功'}
            
        except Exception as e:
            current_app.logger.error(f"删除规格表失败: {spec_id}, 错误: {str(e)}")
            return {'error': f'删除失败: {str(e)}'}
    
    def suggest_corrections(self, df, validation_result):
        """
        为不符合要求的DataFrame提供修改建议
        
        Args:
            df: 原始DataFrame
            validation_result: 验证结果
            
        Returns:
            dict: 修改建议
        """
        suggestions = {}
        
        # 如果验证结果中已经包含建议，直接使用
        if 'suggestions' in validation_result:
            suggestions.update(validation_result['suggestions'])
        
        # 处理数据错误
        if 'data_errors' in validation_result:
            data_errors = validation_result['data_errors']
            
            # 处理item_id的空值
            if 'item_id' in data_errors and data_errors['item_id']['type'] == 'null_values':
                # 尝试生成建议的ID
                suggested_ids = []
                rows = data_errors['item_id']['rows']
                
                for row_num in rows:
                    # 获取实际行索引（行号-2，因为Excel从1开始且有标题行）
                    idx = row_num - 2
                    if 0 <= idx < len(df):
                        # 尝试从产品名称生成ID
                        if 'product_name' in df.columns and not pd.isna(df.iloc[idx]['product_name']):
                            product_name = str(df.iloc[idx]['product_name'])
                            # 使用产品名称的前几个字符 + 行号生成ID
                            name_part = ''.join(e for e in product_name if e.isalnum())[:5].upper()
                            suggested_id = f"{name_part}{row_num:03d}"
                        else:
                            # 如果没有产品名称，使用通用ID
                            suggested_id = f"ITEM{row_num:03d}"
                        suggested_ids.append(suggested_id)
                
                suggestions['item_id_null'] = {
                    'message': '请为以下行添加产品ID',
                    'rows': rows,
                    'suggestion': '可以使用自动生成的ID或根据产品特性创建有意义的ID',
                    'suggested_values': suggested_ids
                }
            
            # 处理item_id的重复值
            if 'item_id' in data_errors and data_errors['item_id']['type'] == 'duplicate_values':
                rows = data_errors['item_id']['rows']
                values = data_errors['item_id']['values']
                
                # 为重复的ID生成新的建议ID
                suggested_ids = []
                for i, row_num in enumerate(rows):
                    if i < len(values):
                        original_id = values[i]
                        # 添加后缀以区分重复ID
                        suggested_id = f"{original_id}_V{i+2}"  # V2, V3, ...
                        suggested_ids.append(suggested_id)
                
                suggestions['item_id_duplicate'] = {
                    'message': '以下行的产品ID重复',
                    'rows': rows,
                    'values': values,
                    'suggestion': '请为重复的产品ID使用唯一值',
                    'suggested_values': suggested_ids
                }
            
            # 处理product_name的空值
            if 'product_name' in data_errors and data_errors['product_name']['type'] == 'null_values':
                rows = data_errors['product_name']['rows']
                
                # 尝试从item_id生成产品名称建议
                suggested_names = []
                for row_num in rows:
                    idx = row_num - 2
                    if 0 <= idx < len(df) and 'item_id' in df.columns and not pd.isna(df.iloc[idx]['item_id']):
                        item_id = str(df.iloc[idx]['item_id'])
                        suggested_name = f"产品 {item_id}"
                    else:
                        suggested_name = f"未命名产品 {row_num}"
                    suggested_names.append(suggested_name)
                
                suggestions['product_name_null'] = {
                    'message': '以下行的产品名称为空',
                    'rows': rows,
                    'suggestion': '建议添加有意义的产品名称',
                    'suggested_values': suggested_names
                }
            
            # 处理standard_unit_price的非数字值
            if 'standard_unit_price' in data_errors and data_errors['standard_unit_price']['type'] == 'invalid_type':
                rows = data_errors['standard_unit_price']['rows']
                values = data_errors['standard_unit_price']['values']
                
                # 尝试修复非数字价格
                suggested_prices = []
                for value in values:
                    # 尝试提取数字部分
                    import re
                    numeric_parts = re.findall(r'\d+\.?\d*', str(value))
                    if numeric_parts:
                        suggested_price = numeric_parts[0]
                    else:
                        suggested_price = "0.00"
                    suggested_prices.append(suggested_price)
                
                suggestions['price_invalid'] = {
                    'message': '以下行的价格格式无效',
                    'rows': rows,
                    'values': values,
                    'suggestion': '请确保价格只包含数字，可以包含小数点但不要包含货币符号或其他字符',
                    'suggested_values': suggested_prices
                }
            
            # 处理standard_unit_price的负值
            if 'standard_unit_price' in data_errors and data_errors['standard_unit_price']['type'] == 'negative_values':
                rows = data_errors['standard_unit_price']['rows']
                values = data_errors['standard_unit_price']['values']
                
                # 将负值转为正值
                suggested_prices = [abs(float(value)) for value in values]
                
                suggestions['price_negative'] = {
                    'message': '以下行的价格为负值',
                    'rows': rows,
                    'values': values,
                    'suggestion': '价格通常应为正值，建议使用以下值',
                    'suggested_values': suggested_prices
                }
        
        # 处理缺失的必需列
        if 'missing_columns' in suggestions:
            missing_cols = suggestions['missing_columns']['columns']
            template_data = {}
            
            # 根据现有数据生成更有意义的模板
            row_count = len(df) if not df.empty else 3
            
            for col in missing_cols:
                if col == 'item_id':
                    # 生成连续的ID
                    template_data[col] = [f"ITEM{i+1:03d}" for i in range(row_count)]
                elif col == 'product_name':
                    # 如果有item_id，使用它来生成产品名称
                    if 'item_id' in df.columns:
                        template_data[col] = [f"产品 {id}" if not pd.isna(id) else f"产品 {i+1}" 
                                             for i, id in enumerate(df['item_id'])]
                    else:
                        template_data[col] = [f"产品 {i+1}" for i in range(row_count)]
                elif col == 'standard_unit_price':
                    # 生成随机价格
                    import random
                    template_data[col] = [round(random.uniform(50, 200), 2) for _ in range(row_count)]
                elif col == 'size':
                    # 常见尺寸
                    sizes = ['S', 'M', 'L', 'XL', 'XXL']
                    template_data[col] = [sizes[i % len(sizes)] for i in range(row_count)]
                elif col == 'color':
                    # 常见颜色
                    colors = ['红色', '蓝色', '绿色', '黑色', '白色', '黄色']
                    template_data[col] = [colors[i % len(colors)] for i in range(row_count)]
                else:
                    template_data[col] = [f"{col} {i+1}" for i in range(row_count)]
            
            suggestions['column_template'] = {
                'message': '您可以添加以下列到您的Excel文件中',
                'template': template_data,
                'example': {col: template_data[col][:3] for col in template_data}  # 只显示前3行作为示例
            }
        
        # 添加列名映射建议
        if hasattr(validation_result, 'mapping_result') and validation_result.mapping_result:
            mapping_result = validation_result.mapping_result
            if hasattr(mapping_result, 'unmapped_columns') and mapping_result.unmapped_columns:
                unmapped_suggestions = {}
                for col in mapping_result.unmapped_columns:
                    if col in mapping_result.suggestions:
                        sugg = mapping_result.suggestions[col]
                        if sugg['suggestions']:
                            unmapped_suggestions[col] = {
                                'message': f"列 '{col}' 无法映射到标准列",
                                'suggestions': sugg['suggestions'],
                                'confidence': sugg['confidence']
                            }
                
                if unmapped_suggestions:
                    suggestions['unmapped_columns'] = {
                        'message': '以下列无法映射到标准列',
                        'columns': unmapped_suggestions
                    }
        
        return suggestions
    
    def generate_sample_excel(self, row_count=5):
        """
        生成示例Excel文件
        
        Args:
            row_count: 生成的行数
            
        Returns:
            pandas.DataFrame: 示例DataFrame
        """
        import random
        
        # 创建示例数据
        sample_data = {}
        
        # 添加所有标准列
        for col in self.required_columns + self.optional_columns:
            if col == 'item_id':
                sample_data[col] = [f"ITEM{i+1:03d}" for i in range(row_count)]
            elif col == 'product_name':
                product_types = ['T恤', '裤子', '外套', '鞋子', '帽子', '手套', '围巾']
                sample_data[col] = [f"{random.choice(product_types)} {i+1}" for i in range(row_count)]
            elif col == 'size':
                sizes = ['S', 'M', 'L', 'XL', 'XXL']
                sample_data[col] = [random.choice(sizes) for _ in range(row_count)]
            elif col == 'color':
                colors = ['红色', '蓝色', '绿色', '黑色', '白色', '黄色', '紫色', '灰色']
                sample_data[col] = [random.choice(colors) for _ in range(row_count)]
            elif col == 'standard_unit_price':
                sample_data[col] = [round(random.uniform(50, 200), 2) for _ in range(row_count)]
            else:
                sample_data[col] = [f"{col} {i+1}" for i in range(row_count)]
        
        # 创建DataFrame
        import pandas as pd
        return pd.DataFrame(sample_data)
    
    def generate_column_mapping_examples(self):
        """
        生成列名映射示例
        
        Returns:
            dict: 列名映射示例
        """
        examples = {}
        
        for standard_col, aliases in self.column_mappings.items():
            # 选择最常用的几个别名
            common_aliases = aliases[:3] if len(aliases) > 3 else aliases
            
            # 添加示例
            examples[standard_col] = {
                'standard': standard_col,
                'aliases': common_aliases,
                'required': standard_col in self.required_columns
            }
        
        return examples
    
    def get_column_mapping_info(self):
        """
        获取列名映射配置信息
        
        Returns:
            dict: 列名映射配置信息
        """
        result = {
            'standard_columns': list(self.column_mappings.keys()),
            'required_columns': self.required_columns,
            'optional_columns': self.optional_columns,
            'column_mappings': self.column_mappings,
            'examples': self.generate_column_mapping_examples()
        }
        
        # 添加更多用户友好的信息
        result['required_columns_description'] = {
            col: {
                'description': self._get_column_description(col),
                'examples': self.column_mappings.get(col, [])[:3]  # 最多显示3个例子
            } for col in self.required_columns
        }
        
        result['optional_columns_description'] = {
            col: {
                'description': self._get_column_description(col),
                'examples': self.column_mappings.get(col, [])[:3]  # 最多显示3个例子
            } for col in self.optional_columns
        }
        
        # 添加格式要求说明
        result['format_requirements'] = {
            'item_id': '产品ID应该是唯一的标识符，不能为空',
            'product_name': '产品名称应该是描述性的文本',
            'standard_unit_price': '标准单价应该是数字，不能为负数',
            'general': '表格应该包含标题行，每列应有明确的列名'
        }
        
        return result
    
    def _get_column_description(self, column_name):
        """
        获取列的描述信息
        
        Args:
            column_name: 列名
            
        Returns:
            str: 列的描述信息
        """
        descriptions = {
            'item_id': '产品的唯一标识符',
            'product_name': '产品的名称或描述',
            'size': '产品的尺寸或规格',
            'color': '产品的颜色',
            'standard_unit_price': '产品的标准单价'
        }
        
        return descriptions.get(column_name, f'{column_name}列')
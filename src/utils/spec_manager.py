"""
产品规格管理模块
负责产品规格表的上传、存储、列表查询和删除
"""

import os
import uuid
import datetime
from werkzeug.utils import secure_filename
from flask import current_app
import pandas as pd

class ProductSpecManager:
    def __init__(self, specs_dir='specs'):
        self.specs_dir = specs_dir
        self.ensure_specs_dir()
        
    def ensure_specs_dir(self):
        """确保规格表存储目录存在"""
        if not os.path.exists(self.specs_dir):
            os.makedirs(self.specs_dir)
            
    def allowed_file(self, filename):
        """检查文件是否为允许的Excel格式"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ['xlsx', 'xls']
               
    def upload_spec(self, file):
        """
        上传产品规格表
        
        Args:
            file: 上传的文件对象
            
        Returns:
            dict: 包含spec_id和filename的字典，或错误信息
        """
        try:
            if not file or file.filename == '':
                return {'error': '未选择文件'}
                
            if not self.allowed_file(file.filename):
                return {'error': '文件格式不支持，请上传Excel文件(.xlsx或.xls)'}
                
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
                    return {'error': 'Excel文件为空或格式不正确'}
                    
                # 检查必需的列是否存在
                required_columns = ['item_id', 'product_name', 'size', 'color', 'standard_unit_price']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    os.remove(file_path)
                    return {'error': f'Excel文件缺少必需的列: {", ".join(missing_columns)}'}
                    
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {'error': f'Excel文件读取失败: {str(e)}'}
            
            # 创建元数据文件
            metadata = {
                'spec_id': spec_id,
                'original_filename': original_filename,
                'stored_filename': stored_filename,
                'upload_time': datetime.datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path),
                'record_count': len(df)
            }
            
            metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return {
                'spec_id': spec_id,
                'filename': original_filename,
                'record_count': len(df),
                'upload_time': metadata['upload_time']
            }
            
        except Exception as e:
            return {'error': f'上传失败: {str(e)}'}
            
    def list_specs(self):
        """
        获取所有已上传的产品规格表列表
        
        Returns:
            list: 规格表信息列表
        """
        try:
            specs = []
            import json
            
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
                                'record_count': metadata.get('record_count', 0)
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
            
    def get_spec_path(self, spec_id):
        """
        根据spec_id获取规格表文件路径
        
        Args:
            spec_id: 规格表ID
            
        Returns:
            str: 文件路径，如果不存在则返回None
        """
        try:
            import json
            metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
            
            if not os.path.exists(metadata_path):
                return None
                
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            excel_path = os.path.join(self.specs_dir, metadata['stored_filename'])
            
            if os.path.exists(excel_path):
                return excel_path
            else:
                return None
                
        except Exception as e:
            current_app.logger.error(f"获取规格表路径失败: {spec_id}, 错误: {str(e)}")
            return None
            
    def delete_spec(self, spec_id):
        """
        删除产品规格表
        
        Args:
            spec_id: 规格表ID
            
        Returns:
            dict: 成功或错误信息
        """
        try:
            import json
            metadata_path = os.path.join(self.specs_dir, f"{spec_id}.json")
            
            if not os.path.exists(metadata_path):
                return {'error': '规格表不存在'}
                
            # 读取元数据获取文件名
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            excel_path = os.path.join(self.specs_dir, metadata['stored_filename'])
            
            # 删除Excel文件
            if os.path.exists(excel_path):
                os.remove(excel_path)
                
            # 删除元数据文件
            os.remove(metadata_path)
            
            return {'message': '规格表删除成功'}
            
        except Exception as e:
            current_app.logger.error(f"删除规格表失败: {spec_id}, 错误: {str(e)}")
            return {'error': f'删除失败: {str(e)}'}
            
    def validate_spec_format(self, file_path):
        """
        验证产品规格表格式
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            dict: 验证结果，包含是否有效和错误信息
        """
        try:
            df = pd.read_excel(file_path)
            
            if df.empty:
                return {'valid': False, 'error': 'Excel文件为空'}
                
            # 检查必需的列
            required_columns = ['item_id', 'product_name', 'size', 'color', 'standard_unit_price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'valid': False, 
                    'error': f'缺少必需的列: {", ".join(missing_columns)}'
                }
                
            # 检查数据类型
            errors = []
            
            # 检查item_id是否为空
            if df['item_id'].isnull().any():
                errors.append('item_id列存在空值')
                
            # 检查standard_unit_price是否为数字
            try:
                pd.to_numeric(df['standard_unit_price'], errors='raise')
            except:
                errors.append('standard_unit_price列包含非数字值')
                
            if errors:
                return {'valid': False, 'error': '; '.join(errors)}
                
            return {
                'valid': True, 
                'record_count': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'文件读取失败: {str(e)}'}


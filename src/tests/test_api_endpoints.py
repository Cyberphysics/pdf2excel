"""
测试API端点
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 模拟Flask应用
class MockFlaskApp:
    def __init__(self):
        self.logger = MagicMock()
        self.root_path = tempfile.mkdtemp()

class TestSpecRoutes(unittest.TestCase):
    """测试规格表相关API端点"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟Flask应用
        self.mock_app = MockFlaskApp()
        
        # 创建测试Excel文件
        self.create_test_excel_files()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.mock_app.root_path)
    
    def create_test_excel_files(self):
        """创建测试用的Excel文件"""
        # 创建有效的规格表
        valid_data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        self.valid_excel_path = os.path.join(self.temp_dir, 'valid_spec.xlsx')
        pd.DataFrame(valid_data).to_excel(self.valid_excel_path, index=False)
        
        # 创建无效的规格表（缺少必需列）
        invalid_data = {
            'item_id': ['ITEM001', 'ITEM002'],
            'description': ['产品A', '产品B']  # 错误的列名
        }
        self.invalid_excel_path = os.path.join(self.temp_dir, 'invalid_spec.xlsx')
        pd.DataFrame(invalid_data).to_excel(self.invalid_excel_path, index=False)
        
        # 创建需要映射的规格表
        mapping_data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        }
        self.mapping_excel_path = os.path.join(self.temp_dir, 'mapping_spec.xlsx')
        pd.DataFrame(mapping_data).to_excel(self.mapping_excel_path, index=False)
    
    @patch('src.routes.spec_routes.current_app')
    def test_column_mapping_info_endpoint(self, mock_current_app):
        """测试获取列名映射配置信息端点"""
        mock_current_app.logger = MagicMock()
        
        # 导入路由模块
        from src.routes.spec_routes import get_column_mapping_info
        
        # 模拟请求
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
            mock_spec_manager.get_column_mapping_info.return_value = {
                'required_columns': ['item_id', 'product_name'],
                'optional_columns': ['size', 'color'],
                'column_mappings': {
                    'item_id': ['产品ID', '商品编号'],
                    'product_name': ['产品名称', '商品名称']
                }
            }
            
            # 调用端点函数
            response, status_code = get_column_mapping_info()
            
            # 验证结果
            self.assertEqual(status_code, 200)
            self.assertIn('required_columns', response.json)
            self.assertIn('optional_columns', response.json)
            self.assertIn('column_mappings', response.json)
    
    @patch('src.routes.spec_routes.current_app')
    def test_column_mapping_examples_endpoint(self, mock_current_app):
        """测试获取列名映射示例端点"""
        mock_current_app.logger = MagicMock()
        
        # 导入路由模块
        from src.routes.spec_routes import get_column_mapping_examples
        
        # 模拟请求
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
            mock_spec_manager.generate_column_mapping_examples.return_value = {
                'item_id': {
                    'standard': 'item_id',
                    'aliases': ['产品ID', '商品编号'],
                    'required': True
                }
            }
            
            mock_spec_manager.generate_sample_excel.return_value = pd.DataFrame({
                'item_id': ['ITEM001'],
                'product_name': ['产品A'],
                'standard_unit_price': [99.99]
            })
            
            # 调用端点函数
            response, status_code = get_column_mapping_examples()
            
            # 验证结果
            self.assertEqual(status_code, 200)
            self.assertIn('examples', response.json)
            self.assertIn('sample_data', response.json)

class TestConfigManagementAPI(unittest.TestCase):
    """测试配置管理API"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟Flask应用
        self.mock_app = MockFlaskApp()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.mock_app.root_path)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.ConfigLoader')
    def test_get_column_mappings_config(self, mock_config_loader, mock_current_app):
        """测试获取列名映射配置API"""
        mock_current_app.logger = MagicMock()
        
        # 模拟配置加载器
        mock_config_loader.get_column_mappings.return_value = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['size', 'color']
        }
        
        # 导入路由函数
        from src.routes.spec_routes import get_column_mappings_config
        
        # 调用端点函数
        response, status_code = get_column_mappings_config()
        
        # 验证结果
        self.assertEqual(status_code, 200)
        response_data = response.json
        self.assertTrue(response_data['success'])
        self.assertIn('config', response_data)
        self.assertIn('column_mappings', response_data['config'])
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.ConfigLoader')
    @patch('src.routes.spec_routes.request')
    def test_update_column_mappings_config(self, mock_request, mock_config_loader, mock_current_app):
        """测试更新列名映射配置API"""
        mock_current_app.logger = MagicMock()
        
        # 模拟请求数据
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号', '货号'],
                'product_name': ['产品名称', '商品名称', '名称']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['size', 'color']
        }
        
        # 模拟配置保存成功
        mock_config_loader.save_column_mappings.return_value = True
        
        # 导入路由函数
        from src.routes.spec_routes import update_column_mappings_config
        
        # 模拟spec_manager
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
            # 调用端点函数
            response, status_code = update_column_mappings_config()
            
            # 验证结果
            self.assertEqual(status_code, 200)
            response_data = response.json
            self.assertTrue(response_data['success'])
            self.assertIn('config', response_data)
            
            # 验证spec_manager.load_column_mappings被调用
            mock_spec_manager.load_column_mappings.assert_called_once()
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.ConfigLoader')
    @patch('src.routes.spec_routes.request')
    def test_update_column_mappings_config_invalid_data(self, mock_request, mock_config_loader, mock_current_app):
        """测试使用无效数据更新列名映射配置API"""
        mock_current_app.logger = MagicMock()
        
        # 模拟无效请求数据（缺少必要键）
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'column_mappings': {},
            'required_columns': []
            # 缺少 optional_columns
        }
        
        # 导入路由函数
        from src.routes.spec_routes import update_column_mappings_config
        
        # 调用端点函数
        response, status_code = update_column_mappings_config()
        
        # 验证结果
        self.assertEqual(status_code, 400)
        response_data = response.json
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error_code'], 'MISSING_CONFIG_KEYS')

class TestMappingConfirmationAPI(unittest.TestCase):
    """测试映射确认API"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟Flask应用
        self.mock_app = MockFlaskApp()
        
        # 创建测试Excel文件
        self.create_test_excel_file()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.mock_app.root_path)
    
    def create_test_excel_file(self):
        """创建测试用的Excel文件"""
        data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        }
        self.test_excel_path = os.path.join(self.temp_dir, 'test_mapping.xlsx')
        pd.DataFrame(data).to_excel(self.test_excel_path, index=False)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.request')
    @patch('src.routes.spec_routes.tempfile')
    @patch('src.routes.spec_routes.pd')
    def test_preview_mapping_auto(self, mock_pd, mock_tempfile, mock_request, mock_current_app):
        """测试自动映射预览API"""
        mock_current_app.logger = MagicMock()
        
        # 模拟请求数据
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'file_id': 'test_file_id'
        }
        
        # 模拟临时文件路径
        mock_tempfile.gettempdir.return_value = self.temp_dir
        
        # 模拟pandas读取Excel
        mock_df = pd.DataFrame({
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        })
        mock_pd.read_excel.return_value = mock_df
        
        # 导入路由函数
        from src.routes.spec_routes import preview_mapping
        
        # 模拟spec_manager
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
            # 模拟映射结果
            mock_mapping_result = MagicMock()
            mock_mapping_result.success = True
            mock_mapping_result.mapped_columns = {
                '产品ID': 'item_id',
                '产品名称': 'product_name',
                '单价': 'standard_unit_price'
            }
            mock_mapping_result.missing_required = []
            mock_mapping_result.unmapped_columns = []
            mock_mapping_result.suggestions = {}
            
            mock_spec_manager.map_columns.return_value = mock_mapping_result
            
            # 创建测试文件
            test_file_path = os.path.join(self.temp_dir, 'test_file_id.xlsx')
            mock_df.to_excel(test_file_path, index=False)
            
            # 调用端点函数
            response, status_code = preview_mapping()
            
            # 验证结果
            self.assertEqual(status_code, 200)
            response_data = response.json
            self.assertEqual(response_data['mapping_type'], 'auto')
            self.assertTrue(response_data['mapping_success'])
            self.assertIn('mapped_columns', response_data)
            self.assertIn('preview_data', response_data)

if __name__ == '__main__':
    unittest.main()
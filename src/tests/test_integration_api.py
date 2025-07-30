"""
集成测试 - API端点集成测试
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from werkzeug.test import Client
from werkzeug.wrappers import Response
from io import BytesIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestAPIIntegration(unittest.TestCase):
    """测试API端点集成"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.temp_dir, 'specs')
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.specs_dir)
        os.makedirs(self.config_dir)
        
        # 创建测试配置
        self.create_test_config()
        
        # 创建测试Excel文件
        self.create_test_excel_files()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_test_config(self):
        """创建测试配置"""
        config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号', '货号'],
                'product_name': ['产品名称', '商品名称', '名称'],
                'size': ['尺寸', '规格', '型号'],
                'color': ['颜色', '色彩'],
                'standard_unit_price': ['标准单价', '单价', '价格']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['size', 'color', 'standard_unit_price']
        }
        
        config_path = os.path.join(self.config_dir, 'column_mappings.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def create_test_excel_files(self):
        """创建测试用的Excel文件"""
        # 有效的规格表
        valid_data = {
            'item_id': ['ITEM001', 'ITEM002', 'ITEM003'],
            'product_name': ['产品A', '产品B', '产品C'],
            'standard_unit_price': [99.99, 129.99, 159.99]
        }
        self.valid_excel_path = os.path.join(self.temp_dir, 'valid_spec.xlsx')
        pd.DataFrame(valid_data).to_excel(self.valid_excel_path, index=False)
        
        # 需要映射的规格表
        mapping_data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        }
        self.mapping_excel_path = os.path.join(self.temp_dir, 'mapping_spec.xlsx')
        pd.DataFrame(mapping_data).to_excel(self.mapping_excel_path, index=False)
        
        # 无效的规格表
        invalid_data = {
            'unknown_column': ['值1', '值2'],
            'another_column': ['值3', '值4']
        }
        self.invalid_excel_path = os.path.join(self.temp_dir, 'invalid_spec.xlsx')
        pd.DataFrame(invalid_data).to_excel(self.invalid_excel_path, index=False)

class TestUploadForMappingAPI(unittest.TestCase):
    """测试上传文件用于映射的API"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir)
        
        # 创建测试配置
        self.create_test_config()
        
        # 创建测试Excel文件
        self.create_test_excel_file()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_test_config(self):
        """创建测试配置"""
        config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称'],
                'standard_unit_price': ['标准单价', '单价']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        config_path = os.path.join(self.config_dir, 'column_mappings.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def create_test_excel_file(self):
        """创建测试用的Excel文件"""
        data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        }
        self.test_excel_path = os.path.join(self.temp_dir, 'test_spec.xlsx')
        pd.DataFrame(data).to_excel(self.test_excel_path, index=False)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.spec_manager')
    @patch('src.routes.spec_routes.request')
    @patch('src.routes.spec_routes.tempfile')
    @patch('src.routes.spec_routes.uuid')
    @patch('src.routes.spec_routes.pd')
    def test_upload_for_mapping_success(self, mock_pd, mock_uuid, mock_tempfile, 
                                       mock_request, mock_spec_manager, mock_current_app):
        """测试成功上传文件用于映射"""
        # 模拟依赖
        mock_current_app.logger = MagicMock()
        mock_uuid.uuid4.return_value = MagicMock()
        mock_uuid.uuid4.return_value.__str__ = lambda x: 'test-file-id'
        mock_tempfile.gettempdir.return_value = self.temp_dir
        
        # 模拟文件上传
        mock_file = MagicMock()
        mock_file.filename = 'test_spec.xlsx'
        mock_file.save = MagicMock()
        mock_request.files = {'file': mock_file}
        
        # 模拟pandas读取Excel
        test_df = pd.DataFrame({
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        })
        mock_pd.read_excel.return_value = test_df
        
        # 模拟spec_manager
        mock_spec_manager.allowed_file.return_value = True
        
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
        mock_spec_manager.get_column_mapping_info.return_value = {
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        # 导入并调用API函数
        from src.routes.spec_routes import upload_for_mapping
        
        response, status_code = upload_for_mapping()
        
        # 验证结果
        self.assertEqual(status_code, 200)
        response_data = response.json
        self.assertEqual(response_data['file_id'], 'test-file-id')
        self.assertEqual(response_data['original_filename'], 'test_spec.xlsx')
        self.assertTrue(response_data['auto_mapping_success'])
        self.assertIn('mapped_columns', response_data)
        self.assertIn('column_mapping_info', response_data)

class TestMappingConfirmationWorkflow(unittest.TestCase):
    """测试映射确认工作流程"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.temp_dir, 'specs')
        os.makedirs(self.specs_dir)
        
        # 创建测试Excel文件
        self.create_test_excel_file()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_test_excel_file(self):
        """创建测试用的Excel文件"""
        data = {
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        }
        self.test_excel_path = os.path.join(self.temp_dir, 'test_spec.xlsx')
        pd.DataFrame(data).to_excel(self.test_excel_path, index=False)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.request')
    @patch('src.routes.spec_routes.tempfile')
    @patch('src.routes.spec_routes.pd')
    def test_preview_mapping_workflow(self, mock_pd, mock_tempfile, mock_request, mock_current_app):
        """测试预览映射工作流程"""
        mock_current_app.logger = MagicMock()
        mock_tempfile.gettempdir.return_value = self.temp_dir
        
        # 模拟请求数据
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'file_id': 'test-file-id'
        }
        
        # 创建测试文件
        test_file_path = os.path.join(self.temp_dir, 'test-file-id.xlsx')
        test_df = pd.DataFrame({
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        })
        test_df.to_excel(test_file_path, index=False)
        
        # 模拟pandas读取Excel
        mock_pd.read_excel.return_value = test_df
        
        # 导入并调用API函数
        from src.routes.spec_routes import preview_mapping
        
        # 模拟spec_manager
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
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
            
            response, status_code = preview_mapping()
            
            # 验证结果
            self.assertEqual(status_code, 200)
            response_data = response.json
            self.assertEqual(response_data['mapping_type'], 'auto')
            self.assertTrue(response_data['mapping_success'])
            self.assertIn('mapped_columns', response_data)
            self.assertIn('preview_data', response_data)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.request')
    @patch('src.routes.spec_routes.tempfile')
    @patch('src.routes.spec_routes.pd')
    @patch('src.routes.spec_routes.uuid')
    @patch('src.routes.spec_routes.datetime')
    @patch('src.routes.spec_routes.json')
    def test_confirm_mapping_workflow(self, mock_json, mock_datetime, mock_uuid, 
                                     mock_pd, mock_tempfile, mock_request, mock_current_app):
        """测试确认映射工作流程"""
        mock_current_app.logger = MagicMock()
        mock_tempfile.gettempdir.return_value = self.temp_dir
        
        # 模拟UUID生成
        mock_uuid.uuid4.return_value = MagicMock()
        mock_uuid.uuid4.return_value.__str__ = lambda x: 'test-spec-id'
        
        # 模拟时间
        mock_datetime.datetime.now.return_value.isoformat.return_value = '2023-01-01T00:00:00'
        
        # 模拟请求数据
        mock_request.is_json = True
        mock_request.get_json.return_value = {
            'file_id': 'test-file-id',
            'mapping_type': 'auto',
            'original_filename': 'test_spec.xlsx'
        }
        
        # 创建测试文件
        test_file_path = os.path.join(self.temp_dir, 'test-file-id.xlsx')
        test_df = pd.DataFrame({
            '产品ID': ['ITEM001', 'ITEM002'],
            '产品名称': ['产品A', '产品B'],
            '单价': [99.99, 129.99]
        })
        test_df.to_excel(test_file_path, index=False)
        
        # 模拟pandas
        mock_pd.read_excel.return_value = test_df
        
        # 导入并调用API函数
        from src.routes.spec_routes import confirm_mapping
        
        # 模拟spec_manager
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
            mock_spec_manager.specs_dir = self.specs_dir
            
            mock_mapping_result = MagicMock()
            mock_mapping_result.success = True
            mock_mapping_result.mapped_columns = {
                '产品ID': 'item_id',
                '产品名称': 'product_name',
                '单价': 'standard_unit_price'
            }
            
            mock_spec_manager.map_columns.return_value = mock_mapping_result
            mock_spec_manager.create_mapped_dataframe.return_value = pd.DataFrame({
                'item_id': ['ITEM001', 'ITEM002'],
                'product_name': ['产品A', '产品B'],
                'standard_unit_price': [99.99, 129.99]
            })
            
            mock_validation_result = {
                'valid': True,
                'record_count': 2,
                'columns': ['item_id', 'product_name', 'standard_unit_price']
            }
            mock_spec_manager.validate_mapped_dataframe.return_value = mock_validation_result
            
            # 模拟文件操作
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.write = MagicMock()
                
                with patch('os.path.getsize', return_value=1024):
                    response, status_code = confirm_mapping()
                    
                    # 验证结果
                    self.assertEqual(status_code, 200)
                    response_data = response.json
                    self.assertTrue(response_data['success'])
                    self.assertEqual(response_data['spec_id'], 'test-spec-id')
                    self.assertEqual(response_data['filename'], 'test_spec.xlsx')
                    self.assertEqual(response_data['mapping_type'], 'auto')

class TestConfigurationManagementWorkflow(unittest.TestCase):
    """测试配置管理工作流程"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir)
        
        # 创建测试配置
        self.create_test_config()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_test_config(self):
        """创建测试配置"""
        config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称'],
                'standard_unit_price': ['标准单价', '单价']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        config_path = os.path.join(self.config_dir, 'column_mappings.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.ConfigLoader')
    def test_get_config_workflow(self, mock_config_loader, mock_current_app):
        """测试获取配置工作流程"""
        mock_current_app.logger = MagicMock()
        
        # 模拟配置加载
        test_config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号'],
                'product_name': ['产品名称', '商品名称']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': []
        }
        
        mock_config_loader.get_column_mappings.return_value = test_config
        
        # 导入并调用API函数
        from src.routes.spec_routes import get_column_mappings_config
        
        response, status_code = get_column_mappings_config()
        
        # 验证结果
        self.assertEqual(status_code, 200)
        response_data = response.json
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['config'], test_config)
    
    @patch('src.routes.spec_routes.current_app')
    @patch('src.routes.spec_routes.ConfigLoader')
    @patch('src.routes.spec_routes.request')
    def test_update_config_workflow(self, mock_request, mock_config_loader, mock_current_app):
        """测试更新配置工作流程"""
        mock_current_app.logger = MagicMock()
        
        # 模拟请求数据
        new_config = {
            'column_mappings': {
                'item_id': ['产品ID', '商品编号', '货号'],
                'product_name': ['产品名称', '商品名称', '名称'],
                'standard_unit_price': ['标准单价', '单价', '价格']
            },
            'required_columns': ['item_id', 'product_name'],
            'optional_columns': ['standard_unit_price']
        }
        
        mock_request.is_json = True
        mock_request.get_json.return_value = new_config
        
        # 模拟配置保存成功
        mock_config_loader.save_column_mappings.return_value = True
        
        # 导入并调用API函数
        from src.routes.spec_routes import update_column_mappings_config
        
        # 模拟spec_manager
        with patch('src.routes.spec_routes.spec_manager') as mock_spec_manager:
            response, status_code = update_column_mappings_config()
            
            # 验证结果
            self.assertEqual(status_code, 200)
            response_data = response.json
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['config'], new_config)
            
            # 验证spec_manager重新加载配置
            mock_spec_manager.load_column_mappings.assert_called_once()

if __name__ == '__main__':
    unittest.main()